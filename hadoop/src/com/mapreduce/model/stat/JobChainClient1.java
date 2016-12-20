package com.mapreduce.model.stat;

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;


// 并行作业链，通过一个reduce求均值

// 问题：给定JobChainClient0中已经分好箱的用户，并行执行作业计算每个箱中用户的平均声望

public class JobChainClient1
{
	public static class AverageReputationMapper extends Mapper<LongWritable, Text, Text, DoubleWritable>
	{
		private static final Text GROUP_ALL_KEY = new Text("Average Reputation:");
		private DoubleWritable outvalue = new DoubleWritable();
		
		@Override
		protected void map(LongWritable key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			// split the line into tokens
			String[] tokens = value.toString().split("\t");
			
			// get the reputation from the third column
			double reputation = Double.parseDouble(tokens[2]);
			
			// set the output value and write to context
			outvalue.set(reputation);
			
			context.write(GROUP_ALL_KEY, outvalue);
		}
	}
	
	public static class AverageReputationReducer extends Reducer<Text, DoubleWritable, Text, DoubleWritable>
	{
		private DoubleWritable outvalue = new DoubleWritable();
		
		@Override
		protected void reduce(Text key, Iterable<DoubleWritable> values,
				Context context)
				throws IOException, InterruptedException
		{
			double sum = 0.0;
			double count = 0;
			for (DoubleWritable dw : values)
			{
				sum += dw.get();
				++count;
			}
			
			outvalue.set(sum/count);
			context.write(key, outvalue);
		}
	}
	
	
	
	

	/**
	 * @param args
	 * @throws InterruptedException 
	 * @throws IOException 
	 */
	public static void main(String[] args) throws Exception
	{
		Configuration conf = new Configuration();
		
		Path belowAvgInputDir = new Path(args[0]);
		Path aboveAvgInputDir = new Path(args[1]);
		
		Path belowAveOutputDir = new Path(args[2]);
		Path aboveAvgOutputDir = new Path(args[3]);
		
		Job belowAvgJob = submitJob(conf, belowAvgInputDir, belowAveOutputDir);
		Job aboveAvgJob = submitJob(conf, aboveAvgInputDir, aboveAvgOutputDir);
		
		// 两个Job都没有完成时，驱动程序休眠
		while (!belowAvgJob.isComplete() || !aboveAvgJob.isComplete())
		{
			Thread.sleep(5000);
		}
		
		if (belowAvgJob.isSuccessful())
		{
			System.out.println("Below Job completed successfully!");
		}
		else
		{
			System.out.println("Below Job failed");
		}
		
		if (aboveAvgJob.isSuccessful())
		{
			System.out.println("Above Job completed successfully!");
		}
		else
		{
			System.out.println("Above Job failed");
		}
	}


	private static Job submitJob(Configuration conf, Path inputDir,
			Path outputDir) throws Exception
	{
		Job job = Job.getInstance(conf, "ParallelJobs");
		job.setJarByClass(JobChainClient1.class);
		
		job.setMapperClass(AverageReputationMapper.class);
		job.setReducerClass(AverageReputationReducer.class);
		
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(DoubleWritable.class);
		
		job.setInputFormatClass(TextInputFormat.class);
		TextInputFormat.addInputPath(job, inputDir);
		
		job.setOutputFormatClass(TextOutputFormat.class);
		TextOutputFormat.setOutputPath(job, outputDir);
		
		// 提交作业
		job.submit();
		return job;
	}

}
