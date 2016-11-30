package com.mapreduce.model.stat;

import java.io.IOException;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NamedNodeMap;
import org.xml.sax.InputSource;

// StackOverflow ��������ظ��Ĺ���
// ��һʾ������������ǰһʾ����������Ϊ��ʾ��������
// ��һʾ���ѻ����������ص���������

// ���⣺����ǰһʾ���������ͨ�������Ӳ����������⡢�ظ������۲��


public class QuestionAnswerBuildingDriver
{
	// mapper ��Ҫ�жϸü�¼�����⻹�ǻظ�
	public static class PostCommentMapper extends Mapper<Object, Text, Text, Text>
	{
		private DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
		private Text outkey = new Text();
		private Text outvalue = new Text();
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Element post = null;
			try
			{
				post = getXmlElementFromString(value.toString());
			}
			catch (Exception e)
			{
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			
			int postType = Integer.parseInt(post.getAttribute("PostTypeId"));
			
			// if postType is 1, it is a question
			if (1 == postType)
			{
				outkey.set(post.getAttribute("Id"));
				outvalue.set("Q" + value.toString());
			}
			else
			{
				// else, it is an answer
				outkey.set(post.getAttribute("ParentId"));
				outvalue.set("A" + value.toString());
			}
			
			context.write(outkey, outvalue);
		}
		
		
		/*
		 * @name �� String ����Ϊ Element
		 */
		private Element getXmlElementFromString(String xml) throws Exception
		{
			DocumentBuilder bldr = dbf.newDocumentBuilder();
			return bldr.parse(new InputSource(new StringReader(xml))).getDocumentElement();
		}	
	}
	
	
	
	
	public static class QuestionAnswerReducer extends Reducer<Text, Text, Text, NullWritable>
	{
		private ArrayList<String> answers = new ArrayList<String>();
		private DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
		private String question = null;
		
		@Override
		protected void reduce(Text key, Iterable<Text> values,
				Context context)
				throws IOException, InterruptedException
		{
			question = null;
			answers.clear();
			
			for (Text t : values)
			{
				if ('Q' == t.charAt(0))
				{
					question = t.toString().substring(1, t.toString().length()).trim();
				}
				else
				{
					answers.add(t.toString().substring(1, t.toString().length()).trim());
				}
			}
			
			if (null != question)
			{
				String  postWithCommentChildren = null;
				try
				{
					postWithCommentChildren = nestElements(question, answers);
				}
				catch (Exception e)
				{
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				
				context.write(new Text(postWithCommentChildren), NullWritable.get());
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
	
	
	
	/**
	 * @param args
	 */
	public static void main(String[] args)
	{
		// TODO Auto-generated method stub

	}

}
