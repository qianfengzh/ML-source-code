package com.hadoopinaction.patentcite;

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.KeyValueTextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

public class CiteCount1 extends Configured implements Tool
{

	public static class MyMap extends Mapper<Text, Text, Text, LongWritable>
	{
		
		
		@Override
		protected void map(Text key, Text value,Context context)
				throws IOException, InterruptedException
		{
			String[] list = value.toString().split(",");
			context.write(key, new LongWritable((long)list.length));
		}
	}
	
	
	
	@Override
	public int run(String[] args) throws Exception
	{
		Configuration conf = getConf();
		Job job = Job.getInstance(conf, "MyJob");
		
		Path in = new Path(args[0]);
		Path out = new Path(args[1]);
		
		FileInputFormat.setInputPaths(job, in);
		FileOutputFormat.setOutputPath(job, out);
		
		job.setMapperClass(MyMap.class);
		job.setInputFormatClass(KeyValueTextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(LongWritable.class);
		
		return job.waitForCompletion(true) ? 0 : 1;
		
	}
	

	/**
	 * @param args
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception
	{
		int res = ToolRunner.run(new Configuration(), new CiteCount1(), args);
		System.exit(res);

	}


}
