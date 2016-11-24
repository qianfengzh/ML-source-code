package com.mapreduce.model.stat;

import java.io.IOException;
import java.util.Random;

import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

// ����ģʽ
// ʹ�� Java ����������ʽ�⣬ͨ�� setup ��������ҵ�����ļ��л�ȡMap������ʽ

public class FilterClient
{
	public static class GrepMapper extends Mapper<Object, Text, NullWritable, Text>
	{
		private String mapRegex = null;
		
		@Override
		protected void setup(Context context)
				throws IOException, InterruptedException
		{
			mapRegex = context.getConfiguration().get("mapregex");
		}
		
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			if (value.toString().matches(mapRegex))
			{
				context.write(NullWritable.get(), value);
			}
		}
	}
	
	// ���������
	// ֻ��map,û��combiner��reducer����ѡȡ�ı�����һ����Сֵʱ��
	// �������лط����д�����С�ļ��������������������ֻreducer����Ŀ
	// Ϊ1������ָ��reducer��Ӧ���࣬���Ҫ����ʹ��һ��identity reducer
	// �򵥵��ֻ������д��һ���ļ��У�����������ʹ�� hadoop fs -cat ��
	// ����ļ��ռ���һ��
	public static class SRSMapper extends Mapper<Object, Text, NullWritable, Text>
	{
		private Random rand = new Random();
		private Double percentage;
		
		@Override
		protected void setup(Context context)
				throws IOException, InterruptedException
		{
			String strPercentage = context.getConfiguration().get("filter_percentage");
			percentage = Double.parseDouble(strPercentage)/100.0;
		}
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			if(rand.nextDouble() < percentage)
			{
				context.write(NullWritable.get(), value);
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
