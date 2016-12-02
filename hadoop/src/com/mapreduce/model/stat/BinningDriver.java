package com.mapreduce.model.stat;

import java.io.IOException;
import java.util.Map;

import org.apache.commons.lang.StringEscapeUtils;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.output.MultipleOutputs;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

// 分箱操作只再 Mapper 阶段进行
// 缺点是将会有多个小文件输出，如分100个箱，且对应有100个mapper,则会输出10000个文件
// 通常会对输出的数据进行后期处理，将其处理为大文件

// 问题：对给定帖子按标签分箱，且对特定的帖子创建一个单独的箱子

public class BinningDriver
{
	public static class BinningMapper extends Mapper<Object, Text, Text, NullWritable>
	{
		private MultipleOutputs<Text, NullWritable> mos = null;
		
		@Override
		protected void setup(Context context)
				throws IOException, InterruptedException
		{
			mos = new MultipleOutputs(context);
		}
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			String rawtags = parsed.get("Tags");
			
			String[] tagTokens = StringEscapeUtils.unescapeHtml(rawtags).split("><");
			
			for (String tag : tagTokens)
			{
				String groomed = tag.replaceAll(">|<", "").toLowerCase();
				
				if (groomed.equalsIgnoreCase("hadoop"))
				{
					mos.write("bins", value, NullWritable.get(), "hadoop-tag");
				}
				if (groomed.equalsIgnoreCase("pig"))
				{
					mos.write("bins", value, NullWritable.get(), "pig-tag");
				}
				if (groomed.equalsIgnoreCase("hive"))
				{
					mos.write("bins", value, NullWritable.get(), "hive-tag");
				}
				if (groomed.equalsIgnoreCase("hbase"))
				{
					mos.write("bins", value, NullWritable.get(), "hbase-tag");
				}
			}
			
			String post = parsed.get("Body");
			if (post.toLowerCase().contains("hadoop"))
			{
				mos.write("bins", value, NullWritable.get(), "hadoop-post");
			}
			
			
			
			
			
			
			
		}
	}
	
	
	
	
	
	
	
	
	
	
	
	
	
	

	/**
	 * @param args
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception
	{
		Configuration conf = new Configuration();
		Job job = Job.getInstance(conf, "Binning");
		
		
		MultipleOutputs.addNamedOutput(job, "bins", TextOutputFormat.class, Text.class, NullWritable.class);
		MultipleOutputs.setCountersEnabled(job, true);
		job.setNumReduceTasks(0);
		
		
		
	}

}
