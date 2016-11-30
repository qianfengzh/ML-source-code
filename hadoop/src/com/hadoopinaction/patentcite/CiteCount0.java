package com.hadoopinaction.patentcite;

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapred.JobClient;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.lib.LongSumReducer;
import org.apache.hadoop.mapred.lib.TokenCountMapper;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;

public class CiteCount0
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
	 */
	public static void main(String[] args)
	{
		//JobClient client = new JobClient();
				Configuration conf = new Configuration();
				JobConf jobConf = new JobConf(conf);
				
				jobConf.setJobName("MyJob");
				Path in = new Path("hdfs://192.168.1.110:9000/user/hadoop/input_data/cite.txt");
				Path out = new Path("hdfs://192.168.1.110:9000/user/hadoop/output_data");
				FileInputFormat.addInputPath(jobConf, in);
				FileOutputFormat.setOutputPath(jobConf, out);
				jobConf.setMapperClass(TokenCountMapper.class);
				jobConf.setCombinerClass(LongSumReducer.class);
				jobConf.setReducerClass(LongSumReducer.class);
				jobConf.setOutputKeyClass(Text.class);
				jobConf.setOutputValueClass(LongWritable.class);
				jobConf.set("key.value.separator.in.input.line", ",");
				
				//client.setConf(jobConf);
				try
				{
					JobClient.runJob(jobConf);
				}
				catch (IOException e)
				{
					e.printStackTrace();
				}

	}

}
