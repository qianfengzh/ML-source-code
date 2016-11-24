package com.cnblogs.vincentzh.hadooptest;

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapred.JobClient;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.lib.LongSumReducer;
import org.apache.hadoop.mapred.lib.TokenCountMapper;

// 通过 Hadoop API 提供的基本实现类实现 WordCount
public class WordCount2
{
	public static void main(String[] args)
	{
		//JobClient client = new JobClient();
		Configuration conf = new Configuration();
		JobConf jobConf = new JobConf(conf);
		
		jobConf.setJobName("WordCount2");
		Path in = new Path("hdfs://192.168.1.110:9000/user/hadoop/input");
		Path out = new Path("hdfs://192.168.1.110:9000/user/hadoop/output");
		FileInputFormat.addInputPath(jobConf, in);
		FileOutputFormat.setOutputPath(jobConf, out);
		jobConf.setMapperClass(TokenCountMapper.class);
		jobConf.setCombinerClass(LongSumReducer.class);
		jobConf.setReducerClass(LongSumReducer.class);
		jobConf.setOutputKeyClass(Text.class);
		jobConf.setOutputValueClass(LongWritable.class);
		
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
