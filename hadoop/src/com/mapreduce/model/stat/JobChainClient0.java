package com.mapreduce.model.stat;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;
import java.util.zip.GZIPInputStream;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.Mapper.Context;
import org.apache.hadoop.mapreduce.filecache.DistributedCache;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.MultipleOutputs;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;
import org.apache.hadoop.mapreduce.lib.reduce.LongSumReducer;


// 给定帖子数据集，每个用户按照发帖数是高于还是低于平均发帖数分类
// 当生成输出时，从一个独立的数据集中获得每个用户的声望及丰富用户信息。


// 实现原理：
// 通过作业链对需求实现进行拆分，前一部分作业通过Job的Counter对用户和发帖总数统计，同时在这一部分作业中，还通过API提供的常用reduce实现类进行combiner优化，
// 后一部分通过分布式缓存丰富用户声望信息，并利用分箱操作对用户进行分箱，并且输出到不同路径。

/*
 * @name 统计用户数和帖子总数
 */
public class JobChainClient0
{
	private static final String MULTIPLE_OUTPUTS_BELOW_NAME="BELOW";
	private static final String MULTIPLE_OUTPUTS_ABOVE_NAME="ABOVE";
	
	// 第一阶段作业：使用 Counter 统计用户总数和帖子总数
	
	public static class UserIdCountMapper extends Mapper<Object, Text, Text, LongWritable>
	{
		public static final String RECORDS_COUNTER_NAME = "Records";
		
		private static final LongWritable ONE = new LongWritable(1);
		private Text outkey = new Text();
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			String userId = parsed.get("OwerUserId");
			
			if (userId != null)
			{
				outkey.set(userId);
				context.write(outkey, ONE);
				//context.getCounter("AVERAGE_CALC_GROUP", RECORDS_COUNTER_NAME).increment(1);
			
				context.getCounter(Record_Counters_Group.RECORDS).increment(1);
			}
		}
	}
	
	// 统计用户数量，并输出 用户/用户发帖数 键值对
	public static class UserIdReducer extends Reducer<Text, LongWritable, Text, LongWritable>
	{
		public static final String USERS_COUNTER_NAME = "Users";
		private LongWritable outvalue = new LongWritable();
		
		@Override
		protected void reduce(Text key, Iterable<LongWritable> values,
				Context context)
				throws IOException, InterruptedException
		{
//			context.getCounter("AVERAGE_CALC_GROUP", USERS_COUNTER_NAME).increment(1);
			context.getCounter(Record_Counters_Group.USERS).increment(1);
			
			int sum = 0;
			for (LongWritable value : values)
			{
				sum += value.get();
			}
			outvalue.set(sum);
			context.write(key, outvalue);
		}
	}
	
	
	
	//--------------------------------------------
	
	// 第二阶段作业：计算所有用户的平均发帖数，并对用户进行分箱
	public static class UserIdBinningMapper extends Mapper<Object, Text, Text, Text>
	{
		public static final String AVERAGE_POSTS_PER_USER = "avg.posts.per.user";
		
		public static void setAveragePostsPerUser(Job job, double avg)
		{
			job.getConfiguration().set(AVERAGE_POSTS_PER_USER, Double.toString(avg));
		}
		
		public static double getAveragePostsPerUser(Configuration conf)
		{
			return Double.parseDouble(conf.get(AVERAGE_POSTS_PER_USER));
		}
		
		
		private double average = 0.0;
		private MultipleOutputs<Text, Text> mos = null;
		private Text outkey = new Text(), outvalue = new Text();
		private HashMap<String, String> userIdToReputation = new HashMap<String, String>();
		
		@Override
		protected void setup(Context context)
				throws IOException, InterruptedException
		{
			average = getAveragePostsPerUser(context.getConfiguration());
			
			mos = new MultipleOutputs<Text, Text>(context);
			
			// 加载分布式缓存
			Path[] files = DistributedCache.getLocalCacheFiles(context.getConfiguration());
			
			for (Path p : files)
			{
				BufferedReader rdr = new BufferedReader(new InputStreamReader(new GZIPInputStream(new FileInputStream(new File(p.toString())))));
				
				String line;
				while ((line = rdr.readLine()) != null)
				{
					Map<String, String> parsed = MRDPUtils.transformXmlToMap(line);
					userIdToReputation.put(parsed.get("id"), parsed.get("Reputation"));
				}
				rdr.close();
			}	
		}
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			String[] tokens = value.toString().split("\t");
			
			String userId = tokens[0];
			int posts = Integer.parseInt(tokens[1]);
			
			outkey.set(userId);
			outvalue.set((long) posts + "\t" + userIdToReputation.get(userId));
			
			if ((double)posts < average)
			{
				mos.write(MULTIPLE_OUTPUTS_BELOW_NAME, outkey, outvalue, MULTIPLE_OUTPUTS_BELOW_NAME+ "/part");
			}
			else
			{
				mos.write(MULTIPLE_OUTPUTS_ABOVE_NAME, outkey, outvalue, MULTIPLE_OUTPUTS_ABOVE_NAME+ "/part");
			}
		}
		
		
		@Override
		protected void cleanup(Context context)
				throws IOException, InterruptedException
		{
			mos.close();
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
		Path postInput = new Path(args[0]);
		Path userInput = new Path(args[1]);
		Path outputDirIntermediate = new Path(args[2] + "_int");
		Path outputDir = new Path(args[2]);
		
		// Serup first job to counter user posts
		Job countingJob = Job.getInstance(conf, "JobChaining-Counting");
		countingJob.setJarByClass(JobChainClient0.class);
		
		countingJob.setMapperClass(UserIdCountMapper.class);
		countingJob.setCombinerClass(LongSumReducer.class);
		countingJob.setReducerClass(UserIdReducer.class);
		
		countingJob.setOutputKeyClass(Text.class);
		countingJob.setOutputValueClass(LongWritable.class);
		
		countingJob.setInputFormatClass(TextInputFormat.class);
		
		TextInputFormat.addInputPath(countingJob, postInput);
		
		countingJob.setOutputFormatClass(TextOutputFormat.class);
		TextOutputFormat.setOutputPath(countingJob, outputDirIntermediate);
		
		int code = countingJob.waitForCompletion(true) ? 0 : 1;
		
		//------------------------------------------------------------------
		
		// 第二段作业
		
		if (0 == code)
		{
			// 通过 counter 计算每个用户的平均发帖数
			double numRecords = (double)countingJob.getCounters().findCounter(Record_Counters_Group.RECORDS).getValue();
			double numUsers = (double)countingJob.getCounters().findCounter(Record_Counters_Group.USERS).getValue();
			double averagePostsPerUser = numRecords / numUsers;
			
			// Setup binning job
			Job binningJob = Job.getInstance(conf, "JobChaining-Binning");
			binningJob.setJarByClass(JobChainClient0.class);
			
			binningJob.setMapperClass(UserIdBinningMapper.class);
			UserIdBinningMapper.setAveragePostsPerUser(binningJob, averagePostsPerUser);
			
			binningJob.setNumReduceTasks(0);
			
			binningJob.setInputFormatClass(TextInputFormat.class);
			TextInputFormat.addInputPath(binningJob, outputDirIntermediate);
			
			// 增加两个 below/above 输出路径
			MultipleOutputs.addNamedOutput(binningJob, MULTIPLE_OUTPUTS_BELOW_NAME, TextOutputFormat.class, Text.class, Text.class);
			MultipleOutputs.addNamedOutput(binningJob, MULTIPLE_OUTPUTS_ABOVE_NAME, TextOutputFormat.class, Text.class, Text.class);
			
			MultipleOutputs.setCountersEnabled(binningJob, true);
			
			TextOutputFormat.setOutputPath(binningJob, outputDir);
			
			// 添加用户缓存文件
			FileStatus[] userFiles = FileSystem.get(conf).listStatus(userInput);
			for (FileStatus status : userFiles)
			{
				DistributedCache.addCacheFile(status.getPath().toUri(), binningJob.getConfiguration());
			}
			
			// 执行该作业
			code = binningJob.waitForCompletion(true) ? 0 :1;
		}
		
		// 清除中间输出结果
		FileSystem.get(conf).delete(outputDirIntermediate, true);
		
		System.exit(code);
	}

}
