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
import org.apache.hadoop.mapreduce.lib.output.MultipleOutputs;

public class JobChainClient1
{
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
					
			}
			
			
			
			
			
			
			
			
			
			
		}
	}
	
	
	
	
	
	
	
	
	
	
	
	

	/**
	 * @param args
	 */
	public static void main(String[] args)
	{
		// TODO Auto-generated method stub

	}

}
