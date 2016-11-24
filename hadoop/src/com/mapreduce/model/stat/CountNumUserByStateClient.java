package com.mapreduce.model.stat;

import java.io.IOException;
import java.lang.reflect.Array;
import java.util.HashSet;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Counter;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

// 使用 Hadoop 用户计数器统计每个州的用户数



public class CountNumUserByStateClient
{
	public static class CountNumUserByStateMapper extends Mapper<Object, Text, NullWritable, NullWritable>
	{
		public static final String STATE_COUNTER_GROUP = "State";
		public static final String UNKNOWN_COUNTER = "Unknown";
		public static final String NULL_OR_EMPTY_COUNTER = "NULL OR EMPTY";
		
		private String[] statesArray = new String[]{
			"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL",
			"GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA",
			"ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE",
			"NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
			"OR", "PA", "RI", "SC", "SF", "TN", "TX", "UT", "VT",
			"VA", "WA", "WV", "WI", "WY"};
		
		private HashSet<String> states = new HashSet<String>(Array.asList(statesArray));
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			String location = parsed.get("Location");
			if (location != null && !location.isEmpty())
			{
				String[] tokens = location.toUpperCase().split("\\s");
				boolean unknown = true;
				for(String state : tokens)
				{
					if(states.contains(state))
					{
						context.getCounter(STATE_COUNTER_GROUP, state).increment(1);
						unknown = false;
						break;
					}
				}
				
				if(unknown)
				{
					context.getCounter(STATE_COUNTER_GROUP, UNKNOWN_COUNTER).increment(1);
				}
			}
			else
			{
				context.getCounter(STATE_COUNTER_GROUP, NULL_OR_EMPTY_COUNTER).increment(1);
			}
		}
	}

	/**
	 * @param args
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception
	{
		Path in = new Path(args[0]);
		Path out = new Path(args[1]);
		
		Configuration conf = new Configuration();
		Job job = Job.getInstance(conf, "Counter");
		
		job.setMapperClass(CountNumUserByStateMapper.class);
		job.setInputFormatClass(TextInputFormat.class);
		FileInputFormat.addInputPath(job, in);
		FileOutputFormat.setOutputPath(job, out);
		
		int code = job.waitForCompletion(true) ? 0 : 1;
		
		if(0 == code)
		{
			for (Counter counter : job.getCounters().getGroup(
					CountNumUserByStateMapper.STATE_COUNTER_GROUP))
			{
				System.out.println(counter.getDisplayName() + "\t" + counter.getValue());
			}
		}
		
		// 删除空的输出目录
		FileSystem.get(conf).delete(out, true);
		System.exit(code);	
	}

}
