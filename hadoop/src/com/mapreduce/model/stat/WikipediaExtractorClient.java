package com.mapreduce.model.stat;

//给定一组用户评论信息，创建一个维基百科URL到一组回复帖子的ID的倒排索引
//XML数据结构
/* <row Id="8189677" PostId="6881722" Text="Have you looked at
* Hadoop? CreationDate="2011-07-30T07:29:33.343" UserId="831878"/>
*
*/

import java.io.IOException;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;



public class WikipediaExtractorClient
{
	public static class WikipediaExtratorMapper extends Mapper<Object, Text, Text, Text>
	{
		private Text link = new Text();
		private Text outkey = new Text();
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			String txt = parsed.get("Body");
			String posttype = parsed.get("PostTypeId");
			String rowid = parsed.get("Id");
			
			// body 为空，或 post 为 1，滤除，无链接
			if(txt == null || (posttype == null && posttype.equals("1")))
			{
				return;
			}
			
			// 解码
			txt = StringEscapedUtils.unescapeHtml(txt.toLowerCase());
			
			link.set(getWikipediaURL(txt));
			outkey.set(rowid);
			context.write(link, outkey);
		}
	}
	
	public static class ConcatenatorReducer extends Reducer<Text, Text, Text, Text>
	{
		private Text result = new Text();
		
		@Override
		protected void reduce(Text key, Iterable<Text> values,
				Context context)
				throws IOException, InterruptedException
		{
			StringBuilder sb = new StringBuilder();
			boolean first = true;
			for (Text id : values)
			{
				if(first)
				{
					first = false;
				}
				else
				{
					sb.append(" ");
				}
				sb.append(id.toString());
			}
			
			result.set(sb.toString());
			context.write(key, result);
		}
	}
	
	
	/**
	 * @param args
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception
	{
		Configuration conf = new Configuration();
		Job job = Job.getInstance(conf, "WikiPediaExtrator");
		
		job.setMapperClass(WikipediaExtratorMapper.class);
		job.setCombinerClass(ConcatenatorReducer.class);
		job.setReducerClass(ConcatenatorReducer.class);
		job.setInputFormatClass(TextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(Text.class);
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		
		System.exit(job.waitForCompletion(true) ? 0 : 1);	
	}

}
