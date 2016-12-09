package com.mapreduce.model.stat;

import java.io.IOException;
import java.util.Map;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;

// 给定帖子数据集，每个用户按照发帖数是高于还是低于平均发帖数分类，
// 当生成输出时，从一个独立的数据集中获得每个用户的声望及丰富用户信息。



public class JobChainClient0
{
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
	
	
	
	
	
	
	
	
	

	/**
	 * @param args
	 */
	public static void main(String[] args)
	{
		// TODO Auto-generated method stub

	}

}
