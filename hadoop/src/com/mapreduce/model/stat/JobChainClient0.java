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


// �����������ݼ���ÿ���û����շ������Ǹ��ڻ��ǵ���ƽ������������
// ���������ʱ����һ�����������ݼ��л��ÿ���û����������ḻ�û���Ϣ��


// ʵ��ԭ��
// ͨ����ҵ��������ʵ�ֽ��в�֣�ǰһ������ҵͨ��Job��Counter���û��ͷ�������ͳ�ƣ�ͬʱ����һ������ҵ�У���ͨ��API�ṩ�ĳ���reduceʵ�������combiner�Ż���
// ��һ����ͨ���ֲ�ʽ����ḻ�û�������Ϣ�������÷���������û����з��䣬�����������ͬ·����

/*
 * @name ͳ���û�������������
 */
public class JobChainClient0
{
	private static final String MULTIPLE_OUTPUTS_BELOW_NAME="BELOW";
	private static final String MULTIPLE_OUTPUTS_ABOVE_NAME="ABOVE";
	
	// ��һ�׶���ҵ��ʹ�� Counter ͳ���û���������������
	
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
	
	// ͳ���û������������ �û�/�û������� ��ֵ��
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
	
	// �ڶ��׶���ҵ�����������û���ƽ���������������û����з���
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
			
			// ���طֲ�ʽ����
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
		
		// �ڶ�����ҵ
		
		if (0 == code)
		{
			// ͨ�� counter ����ÿ���û���ƽ��������
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
			
			// �������� below/above ���·��
			MultipleOutputs.addNamedOutput(binningJob, MULTIPLE_OUTPUTS_BELOW_NAME, TextOutputFormat.class, Text.class, Text.class);
			MultipleOutputs.addNamedOutput(binningJob, MULTIPLE_OUTPUTS_ABOVE_NAME, TextOutputFormat.class, Text.class, Text.class);
			
			MultipleOutputs.setCountersEnabled(binningJob, true);
			
			TextOutputFormat.setOutputPath(binningJob, outputDir);
			
			// ����û������ļ�
			FileStatus[] userFiles = FileSystem.get(conf).listStatus(userInput);
			for (FileStatus status : userFiles)
			{
				DistributedCache.addCacheFile(status.getPath().toUri(), binningJob.getConfiguration());
			}
			
			// ִ�и���ҵ
			code = binningJob.waitForCompletion(true) ? 0 :1;
		}
		
		// ����м�������
		FileSystem.get(conf).delete(outputDirIntermediate, true);
		
		System.exit(code);
	}

}
