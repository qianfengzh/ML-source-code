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
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.filecache.DistributedCache;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

public class ReplicatedJoinDriver
{
	public static class ReplicatedJoinMapper extends Mapper<Object, Text, Text, Text>
	{
		private static final Text EMPTY_TEXT = new Text("");
		private HashMap<String, String> userIdToInfo = new HashMap<String, String>();
		
		private Text outvalue = new Text();
		private String joinType = null;
		
		@Override
		protected void setup(Context context)
				throws IOException, InterruptedException
		{
			Path[] files = DistributedCache.getLocalCacheFiles(context.getConfiguration());
			for (Path p : files)
			{
				BufferedReader rdr = new BufferedReader(new InputStreamReader(new GZIPInputStream(new FileInputStream(new File(p.toString())))));
				String line = null;
				
				while ((line = rdr.readLine()) != null)
				{
					Map<String, String> parsed = MRDPUtils.transformXmlToMap(line);
					String userId = parsed.get("Id");
					
					userIdToInfo.put(userId, line);
				}
			}
			joinType = context.getConfiguration().get("join.type");
		}
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			String userId = parsed.get("UserId");
			String userInfomation = userIdToInfo.get(userId);
			
			if (userInfomation != null)
			{
				outvalue.set(userInfomation);
				context.write(value, outvalue);
			}
			else if(joinType.equalsIgnoreCase("leftouter"))
			{
				context.write(value, EMPTY_TEXT);
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
		Job job = Job.getInstance(conf, "ReplicatedJoinDriver");
		
		job.setJarByClass(ReplicatedJoinDriver.class);
		job.setMapperClass(ReplicatedJoinMapper.class);
		
		job.setInputFormatClass(TextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(Text.class);
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		job.setNumReduceTasks(0);
		
		System.exit(job.waitForCompletion(true) ? 0 : 1);
	}

}
