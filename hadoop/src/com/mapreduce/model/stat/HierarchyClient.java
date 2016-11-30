package com.mapreduce.model.stat;

import java.io.IOException;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.MultipleInputs;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;
import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NamedNodeMap;
import org.xml.sax.InputSource;

/*
 * 适用范围：
 * 	数据源被外键链接
 * 	数据是结构化的并且是基于行的
 * （即多个数据源输入）
 */

// MultipleInputs类允许为每一个输入指定不同的路径及不同的Mapper类

// 性能分析：
//	1、mapper发送了多少数据给reducer
//	2、reducer构建的对象占用了多少内存

// 问题：给定一个帖子和评论的列表，创建一个结构化的XML层次结构，
// 嵌套地表示帖子及其县官评论。

public class HierarchyClient
{

	/**
	 * @param args
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception
	{
		Configuration conf = new Configuration();
		Job job = Job.getInstance(conf, "Hierachy");
		
		// 通过 MultipleInputs 类为不同的数据源配置不同的 Mapper 处理类
		MultipleInputs.addInputPath(job, new Path(args[0]),
				TextInputFormat.class, PostMapper.class);
		
		MultipleInputs.addInputPath(job, new Path(args[1]),
				TextInputFormat.class, CommentMapper.class);
		
		job.setReducerClass(UserJoinReducer.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(NullWritable.class);
		TextOutputFormat.setOutputPath(job, new Path(args[2]));
		
		System.exit(job.waitForCompletion(true) ? 0 : 2);
	}
	
	
	// 两个不同的 Mapper 处理类中，均提取帖子ID作为输出键
	// 同时再输入值加上前缀（P/C），标识记录所属的数据集
	public static class PostMapper extends Mapper<Object, Text, Text, Text>
	{
		private Text outkey = new Text();
		private Text outvalue = new Text();
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			outkey.set(parsed.get("Id"));
			outvalue.set("P" + value.toString());
			context.write(outkey, outvalue);
		}
	}
	
	public static class CommentMapper extends Mapper<Object, Text, Text, Text>
	{
		private Text outkey = new Text();
		private Text outvalue = new Text();
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			outkey.set(parsed.get("PostId"));
			outvalue.set("C" + value.toString());
			context.write(outkey, outvalue);
		}
	}
	
	
	// 构建分层的 XML 对象，其中帖子为父元素，评论作为子元素
	public static class UserJoinReducer extends Reducer<Text, Text, Text, NullWritable>
	{
		private ArrayList<String> comments = new ArrayList<String>();
		private DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
		private String post = null;
		
		@Override
		protected void reduce(Text key, Iterable<Text> values,
				Context context)
				throws IOException, InterruptedException
		{
			comments.clear();
			
			for (Text t : values)
			{
				if ('P' == t.charAt(0))
				{
					post = t.toString().substring(1, t.toString().length()).trim();
				}
				else
				{
					comments.add(t.toString().substring(1, t.toString().length()).trim());
				}
			}
			
			
			if (null != post)
			{
				String postWithComentChildren = null;
				try
				{
					postWithComentChildren = nestElements(post, comments);
				}
				catch (Exception e)
				{
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				
				context.write(new Text(postWithComentChildren), NullWritable.get());
			}
		}
		
		
		/*
		 * @name 创建XML字符串作为输出
		 */
		private String nestElements(String post, List<String> comments) throws Exception
		{
			// 创建新的 document 用于构建 XML
			DocumentBuilder bldr = dbf.newDocumentBuilder();
			Document doc = bldr.newDocument();
			
			// 复制父节点到document
			Element postEl = getXmlElementFromString(post);
			Element toAddPostEl = doc.createElement("post");
			
			copyAttributesToElement(postEl.getAttributes(), toAddPostEl);
			
			// 将每个 comment 复制进这个 post 节点中
			for (String commentXml : comments)
			{
				Element commentEl = getXmlElementFromString(commentXml);
				Element toAddCommentEl = doc.createElement("comments");
				copyAttributesToElement(commentEl.getAttributes(), toAddCommentEl);
				
				// Add the copied comment to the post element
				toAddPostEl.appendChild(toAddCommentEl);
			}
			
			// Add the post element to the document
			doc.appendChild(toAddPostEl);
			
			// Transform the  document into a String of XML and return
			return transformDocumentToString(doc);
		}
		
		
		/*
		 * @name 将 String 解析为 Element
		 */
		private Element getXmlElementFromString(String xml) throws Exception
		{
			DocumentBuilder bldr = dbf.newDocumentBuilder();
			return bldr.parse(new InputSource(new StringReader(xml))).getDocumentElement();
		}
		
		
		/*
		 * @name 复制 Element 到 Node 中
		 */
		private void copyAttributesToElement(NamedNodeMap attributes, Element element)
		{
			for (int i=0; i<attributes.getLength(); ++i)
			{
				Attr toCopy = (Attr) attributes.item(i);
				element.setAttribute(toCopy.getName(), toCopy.getValue());
			}
		}
		
		/*
		 * @name 解析 Document 为 String
		 */
		private String transformDocumentToString(Document doc) throws Exception
		{
			TransformerFactory tf = TransformerFactory.newInstance();
			Transformer transformer = tf.newTransformer();
			transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, "yes");
			StringWriter writer = new StringWriter();
			transformer.transform(new DOMSource(doc), new StreamResult(writer));
			
			return writer.getBuffer().toString().replace("\n|\r", "");
		}
	}
}
