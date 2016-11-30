package com.mapreduce.model.stat;

import java.io.IOException;
import java.util.Map;
import java.util.TreeMap;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

// 给定一个用户信息列表，输出其基于用户声望值的 Top10 用户信息

public class TopTenClient
{
	public static class TopTenMapper extends Mapper<Object, Text, NullWritable, Text>
	{
		private TreeMap<Integer, Text> repToRecordMap = new TreeMap<Integer, Text>();
		
		@Override
		// 获取每个 splitInput 的Top10
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			// String userId = parsed.get("Id");
			String reputation = parsed.get("Reputation");
			
			repToRecordMap.put(Integer.parseInt(reputation), new Text(value));
			
			if (10 < repToRecordMap.size())
			{
				repToRecordMap.remove(repToRecordMap.firstKey());
			}	
		}
		
		@Override
		protected void cleanup(Context context)
				throws IOException, InterruptedException
		{
			for (Text t : repToRecordMap.values())
			{
				context.write(NullWritable.get(), t);
			}	
		}
	}
	
	
	
	
	public static class TopTenReducer extends Reducer<NullWritable, Text, NullWritable, Text>
	{
		private TreeMap<Integer, Text> repToRecordMap = new TreeMap<Integer, Text>();
		
		@Override
		protected void reduce(NullWritable key, Iterable<Text> values,
				Context context)
				throws IOException, InterruptedException
		{
			for (Text value : values)
			{
				Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
				
				repToRecordMap.put(Integer.parseInt(parsed.get("Reputation")), new Text(value));
				
				if (10 < repToRecordMap.size())
				{
					repToRecordMap.remove(repToRecordMap.firstKey());
				}
			}
			
			for (Text t : repToRecordMap.descendingMap().values())
			{
				context.write(NullWritable.get(), t);
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
		Job job = Job.getInstance(conf, "TopTen");
		
		job.setMapperClass(TopTenMapper.class);
		job.setReducerClass(TopTenReducer.class);
		job.setInputFormatClass(TextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(NullWritable.class);
		job.setOutputValueClass(Text.class);
		
		job.setNumReduceTasks(1);
		
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		
		System.exit(job.waitForCompletion(true) ? 0 :1);
	}
}
