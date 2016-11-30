package com.mapreduce.model.stat;

import java.io.IOException;
import java.util.Random;

import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

// 过滤模式
// 使用 Java 内置正则表达式库，通过 setup 函数从作业配置文件中获取Map正则表达式

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
	
	// 简单随机抽样
	// 只有map,没有combiner和reducer，当选取的比例是一个较小值时，
	// 输出结果中回发现有大量的小文件，如遇到这种情况，这只reducer的数目
	// 为1，并不指定reducer对应的类，这就要求框架使用一个identity reducer
	// 简单地手机输出并写道一个文件中，后续处理是使用 hadoop fs -cat 将
	// 输出文件收集到一起。
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
