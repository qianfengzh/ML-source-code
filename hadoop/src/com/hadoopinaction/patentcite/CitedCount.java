package com.hadoopinaction.patentcite;

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.KeyValueTextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

public class CitedCount
{
	public static class MyMap extends Mapper<Text, Text, Text, IntWritable>
	{
		private IntWritable one = new IntWritable(1);
		@Override
		protected void map(Text key, Text value, Context context)
				throws IOException, InterruptedException
		{
			// context.write(value, key);
			context.write(key, one);
		}
	}
	
	public static class MyReduce extends Reducer<Text, IntWritable, Text, IntWritable>
	{
		@Override
		protected void reduce(Text key, Iterable<IntWritable> value, Context context)
				throws IOException, InterruptedException
		{
//			String csv = "";
//			
//			for(Text val : value)
//			{
//				if (csv.length()>0)
//				{
//					csv += ",";
//				}
//				csv += val.toString();
//			}
//			context.write(key, new Text(csv));		
			
			int sum = 0;
			
			for(IntWritable one : value)
			{
				sum += one.get();
			}
			context.write(key, new IntWritable(sum));
		}
	}
	
	
	/**
	 * @param args
	 * @throws IOException 
	 * @throws Exception 
	 * @throws ClassNotFoundException 
	 */
	public static void main(String[] args) throws IOException, ClassNotFoundException, Exception
	{
		Configuration conf = new Configuration();
		Job job = Job.getInstance(conf, "MyJob");
		conf.set("mapreduce.input.keyvaluelinerecordreader.key.value.separator", ",");
		
		Path in = new Path("hdfs://192.168.1.110:9000/user/hadoop/input_data/cite.txt");
		Path out = new Path("hdfs://192.168.1.110:9000/user/hadoop/output_data");
		
		job.setJarByClass(CitedCount.class);
		FileInputFormat.setInputPaths(job, in);
		FileOutputFormat.setOutputPath(job, out);
		
		job.setMapperClass(MyMap.class);
		job.setCombinerClass(MyReduce.class);
		job.setReducerClass(MyReduce.class);
		job.setInputFormatClass(KeyValueTextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(IntWritable.class);
		
		
		System.exit(job.waitForCompletion(true) ? 0 : 1);
	}

}
