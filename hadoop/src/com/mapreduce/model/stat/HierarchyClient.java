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
 * ���÷�Χ��
 * 	����Դ���������
 * 	�����ǽṹ���Ĳ����ǻ����е�
 * �����������Դ���룩
 */

// MultipleInputs������Ϊÿһ������ָ����ͬ��·������ͬ��Mapper��

// ���ܷ�����
//	1��mapper�����˶������ݸ�reducer
//	2��reducer�����Ķ���ռ���˶����ڴ�

// ���⣺����һ�����Ӻ����۵��б�����һ���ṹ����XML��νṹ��
// Ƕ�׵ر�ʾ���Ӽ����ع����ۡ�

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
		
		// ͨ�� MultipleInputs ��Ϊ��ͬ������Դ���ò�ͬ�� Mapper ������
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
	
	
	// ������ͬ�� Mapper �������У�����ȡ����ID��Ϊ�����
	// ͬʱ������ֵ����ǰ׺��P/C������ʶ��¼���������ݼ�
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
	
	
	// �����ֲ�� XML ������������Ϊ��Ԫ�أ�������Ϊ��Ԫ��
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
		 * @name ����XML�ַ�����Ϊ���
		 */
		private String nestElements(String post, List<String> comments) throws Exception
		{
			// �����µ� document ���ڹ��� XML
			DocumentBuilder bldr = dbf.newDocumentBuilder();
			Document doc = bldr.newDocument();
			
			// ���Ƹ��ڵ㵽document
			Element postEl = getXmlElementFromString(post);
			Element toAddPostEl = doc.createElement("post");
			
			copyAttributesToElement(postEl.getAttributes(), toAddPostEl);
			
			// ��ÿ�� comment ���ƽ���� post �ڵ���
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
		 * @name �� String ����Ϊ Element
		 */
		private Element getXmlElementFromString(String xml) throws Exception
		{
			DocumentBuilder bldr = dbf.newDocumentBuilder();
			return bldr.parse(new InputSource(new StringReader(xml))).getDocumentElement();
		}
		
		
		/*
		 * @name ���� Element �� Node ��
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
		 * @name ���� Document Ϊ String
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
