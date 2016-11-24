package com.mapreduce.model.stat;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
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

// 定义数值概要 Mapper
public class MinMaxCountClient
{
	public static class MinMaxCountMapper extends Mapper<Object, Text, Text, MinMaxCountTuple>
	{
		// Our output key and value Writable
		private Text outUserId = new Text();
		private MinMaxCountTuple outTuple = new MinMaxCountTuple();
		
		// This object will format the creation date string into a Date object
		private final static SimpleDateFormat frmt = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS");
		private Date creationDate;
				
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			// Grab the "CreationDate" field since it is what we are finding
			// the min and max value of
			String strDate = parsed.get("CreationDate");
			
			// Grab the "UserId" field since it is what we are grouping by
			String userId = parsed.get("UserId");
			
			// Parse the string into a Date object
			
				try
				{
					creationDate = frmt.parse(strDate);
				}
				catch (ParseException e)
				{
					e.printStackTrace();
				}
			
			// Set the minimum and maximum date values to the creationDate
			outTuple.setMin(creationDate);
			outTuple.setMax(creationDate);
			
			// Set the comment count to 1
			outTuple.setCount(1);
			
			//Set our user ID as the output key
			outUserId.set(userId);
			
			// Write out the hour and the average comment length
			context.write(outUserId, outTuple);		
		}
	}
	
	
	public static class MinMaxCountReducer extends Reducer<Text, MinMaxCountTuple, Text, MinMaxCountTuple>
	{
		// 声明输出变量
		private MinMaxCountTuple result = new MinMaxCountTuple();
		
		@Override
		protected void reduce(Text key, Iterable<MinMaxCountTuple> values,
				Context context)
				throws IOException, InterruptedException
		{
			// 初始化结果
			result.setMin(null);
			result.setMax(null);
			result.setCount(0);
			long sum = 0;
			
			for(MinMaxCountTuple value : values)
			{
				if(null == value.getMin() || value.getMin().compareTo(result.getMin()) < 0)
				{
					result.setMin(value.getMin());
				}
				
				if(null == value.getMax() || value.getMax().compareTo(result.getMax()) > 0)
				{
					result.setMax(value.getMax());
				}
				
				sum += value.getCount();
			}
			result.setCount(sum);
			context.write(key, result);
		}
	}
	

	public static void main(String[] args) throws Exception
	{
		Configuration conf = new Configuration();
		Job job = Job.getInstance(conf, "MinMaxCount");
		
		job.setJarByClass(MinMaxCountClient.class);
		job.setMapperClass(MinMaxCountMapper.class);
		job.setReducerClass(MinMaxCountReducer.class);
		job.setInputFormatClass(TextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(MinMaxCountTuple.class);
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		
		System.exit(job.waitForCompletion(true) ? 0 : 1);
	}
}
























