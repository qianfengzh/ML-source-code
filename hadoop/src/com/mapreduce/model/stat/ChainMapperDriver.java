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
import org.apache.hadoop.mapreduce.filecache.DistributedCache;
import org.apache.hadoop.mapreduce.lib.chain.ChainMapper;
import org.apache.hadoop.mapreduce.lib.chain.ChainReducer;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.MultipleOutputs;
import org.apache.hadoop.mapreduce.lib.output.NullOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;


//问题：给定用户帖子和用户信息的数据集，依据5000声望将用户进行分箱

// reducer 后面的 mapper 一般不用 ChainMapper添加，而是用 ChainReducer添加

public class ChainMapperDriver
{
	private static final String MULTIPLE_OUTPUTS_BELOW_500 = "BELOW_500";
	private static final String MULTIPLE_OUTPUTS_ABOVE_500 = "ABOVE_500";
	
	
	// 解析数据 Mapper
	public static class UserIdCountMapper extends Mapper<Object, Text, Text, LongWritable>
	{
		private static final LongWritable ONE = new LongWritable(1);
		private Text outkey = new Text();
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			outkey.set(parsed.get("OwnerUserId"));
			context.write(outkey, ONE);
		}
	}
	
	
	// 复制连接，丰富声望到数据集
	public static class UserIdReputationEnrichmentMapper extends Mapper<Text, LongWritable, Text, LongWritable>
	{
		private Text outkey = new Text();
		private HashMap<String, String> userIdToReputation = new HashMap<String, String>();
		
		
		@Override
		protected void setup(Context context)
				throws IOException, InterruptedException
		{
			Path[] files = DistributedCache.getLocalCacheFiles(context.getConfiguration());
			
			for (Path p : files)
			{
				BufferedReader rdr = new BufferedReader(new InputStreamReader(new GZIPInputStream(new FileInputStream(new File(p.toString())))));
				
				String line;
				while ((line=rdr.readLine()) != null)
				{
					Map<String, String> parsed = MRDPUtils.transformXmlToMap(line);
					userIdToReputation.put(parsed.get("Id"), parsed.get("Reputation"));
				}
			}
		}
		
		@Override
		protected void map(Text key, LongWritable value,
				Context context)
				throws IOException, InterruptedException
		{
			String reputation = userIdToReputation.get(key.toString());
			
			if (null != reputation)
			{
				outkey.set(key.toString() + "\t" + reputation);
				context.write(outkey, value);
			}
		}
	}
	
	
	// 求和 Reducer
	public static class LongSumReducer extends Reducer<Text, LongWritable, Text, LongWritable>
	{
		private LongWritable outvalue = new LongWritable();
		
		@Override
		protected void reduce(Text key, Iterable<LongWritable> values,
				Context context)
				throws IOException, InterruptedException
		{
			int sum = 0;
			for (LongWritable value : values)
			{
				sum += value.get();
			}
			outvalue.set(sum);
			context.write(key, outvalue);
		}
	}
	
	
	// 分箱 Mapper
	public static class UserIdBinningMapper extends Mapper<Text, LongWritable, Text, LongWritable>
	{
		private MultipleOutputs mos = null;

		@Override
		protected void setup(Context context)
				throws IOException, InterruptedException
		{
			mos = new MultipleOutputs(context);
		}
		
		@Override
		protected void map(Text key, LongWritable value,
				Context context)
				throws IOException, InterruptedException
		{
			if (Integer.parseInt(value.toString().split("\t")[1]) < 5000)
			{
				mos.write(MULTIPLE_OUTPUTS_BELOW_500, key, value);
			}
			else
			{
				mos.write(MULTIPLE_OUTPUTS_ABOVE_500, key, value);
			}
		}
		
		
		@Override
		protected void cleanup(
				Context context)
				throws IOException, InterruptedException
		{
			mos.close();
		}
	}
	
	
	
	
	/**
	 * @name Driver
	 * @param args
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception
	{
		Configuration conf = new Configuration();
		Job job = Job.getInstance(conf, "ChainMapperDriver");
		
		Path postInput = new Path(args[0]);
		Path userInput = new Path(args[1]);
		Path outputDir = new Path(args[2]);
		
		ChainMapper.addMapper(job,UserIdCountMapper.class
				,LongWritable.class, Text.class, Text.class, LongWritable.class
				,new Configuration(false));
		ChainMapper.addMapper(job, UserIdReputationEnrichmentMapper.class
				,Text.class, LongWritable.class, Text.class, LongWritable.class
				,new Configuration(false));
		ChainReducer.setReducer(job, LongSumReducer.class
				,Text.class, LongWritable.class, Text.class, LongWritable.class
				,new Configuration(false));
		ChainReducer.addMapper(job, UserIdBinningMapper.class
				,Text.class, LongWritable.class, Text.class, LongWritable.class
				,new Configuration(false));
		
		job.setCombinerClass(LongSumReducer.class);
		
		job.setInputFormatClass(TextInputFormat.class);
		TextInputFormat.addInputPath(job, postInput);
		job.setOutputFormatClass(NullOutputFormat.class);
		job.setOutputValueClass(LongWritable.class);
		job.setOutputKeyClass(Text.class);
		
		FileOutputFormat.setOutputPath(job, outputDir);
		MultipleOutputs.addNamedOutput(job, MULTIPLE_OUTPUTS_BELOW_500
				,TextOutputFormat.class, Text.class, LongWritable.class);
		MultipleOutputs.addNamedOutput(job, MULTIPLE_OUTPUTS_ABOVE_500
				,TextOutputFormat.class, Text.class, LongWritable.class);
		
		
		
		// 添加分布式缓存文件
		FileStatus[] userFiles = FileSystem.get(conf).listStatus(userInput);
		for (FileStatus status : userFiles)
		{
			DistributedCache.addCacheFile(status.getPath().toUri(),conf);
		}
		
		System.exit(job.waitForCompletion(true) ? 0 : 1);
	}

}
