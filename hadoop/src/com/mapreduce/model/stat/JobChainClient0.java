package com.mapreduce.model.stat;

import java.io.IOException;
import java.util.Map;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;

// �����������ݼ���ÿ���û����շ������Ǹ��ڻ��ǵ���ƽ�����������࣬
// ���������ʱ����һ�����������ݼ��л��ÿ���û����������ḻ�û���Ϣ��



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
