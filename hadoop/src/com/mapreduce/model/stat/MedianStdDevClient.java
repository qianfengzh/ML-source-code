package com.mapreduce.model.stat;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.Map;
import java.util.Map.Entry;
import java.util.TreeMap;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

// 对给定的用户评论列表，确定一天按小时的评论长度的中位数和标准差
//XML数据结构
/* <row Id="8189677" PostId="6881722" Text="Have you looked at
* Hadoop? CreationDate="2011-07-30T07:29:33.343" UserId="831878"/>
*
*/


public class MedianStdDevClient
{
	public static class MedianStdDevMapper extends Mapper<Object, Text, IntWritable, IntWritable>
	{
		private IntWritable outHour = new IntWritable();
		private IntWritable outCommentLength = new IntWritable();
		private final static SimpleDateFormat frmt = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSS");
		private Date creationDate;
		
		@SuppressWarnings("deprecation")
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			String strDate = parsed.get("CreationDate");
			String text = parsed.get("Text");
			try
			{
				creationDate = frmt.parse(strDate);
			}
			catch (ParseException e)
			{
				e.printStackTrace();
			}
			
			outHour.set(creationDate.getHours());
			outCommentLength.set(text.length());
			context.write(outHour, outCommentLength);		
		}
	}
	
	public static class MedianStdDevReducer extends Reducer<IntWritable, IntWritable, IntWritable, MedianStdDevTuple>
	{
		private MedianStdDevTuple result = new MedianStdDevTuple();
		private ArrayList<Float> commentLengths = new ArrayList<Float>();
		
		@Override
		protected void reduce(IntWritable key, Iterable<IntWritable> values,
				Context context)
				throws IOException, InterruptedException
		{
			float sum = 0;
			float count = 0;
			
			commentLengths.clear();
			result.setStdDev(0);
			
			for(IntWritable val:values)
			{
				commentLengths.add((float)val.get());
				sum += val.get();
				++count;
			}
			
			Collections.sort(commentLengths);
			if(0 == count%2)
			{
				result.setMedian((commentLengths.get((int)count/2-1) + 
						commentLengths.get((int)count/2)) / 2.0f);
			}
			else
			{
				result.setMedian(commentLengths.get((int)count/2));
			}
			
			float mean = sum / count;
			float sumOfSquares = 0.0f;
			for (Float f:commentLengths)
			{
				sumOfSquares += (f-mean)*(f-mean);
			}
			result.setStdDev((float)Math.sqrt(sumOfSquares/(count-1)));
			context.write(key, result);		
		}
	}
	
	
	//---------------------------------------------------------------------------------
	// 添加 combiner 的中位数和标准差实现
	// 原理：将评论长度和不同长度的个数，以map的数据结构形式存放入list中
	
	public static class MyMapper extends Mapper<Object, Text, IntWritable, SortedMapWritable<IntWritable, LongWritable>>
	{
		private IntWritable outHour = new IntWritable();
		private IntWritable commentLength = new IntWritable();
		private static final LongWritable ONE = new LongWritable(1);
		private final static SimpleDateFormat frmt = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSS");
		private Date creationDate;
		
		@SuppressWarnings("deprecation")
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			String strDate = parsed.get("CreationDate");
			String text = parsed.get("Text");
			try
			{
				creationDate = frmt.parse(strDate);
			}
			catch (ParseException e)
			{
				e.printStackTrace();
			}
			outHour.set(creationDate.getHours());
			commentLength.set(text.length());
			SortedMapWritable<IntWritable, LongWritable> outCommentLength = new SortedMapWritable<IntWritable, LongWritable>();
			outCommentLength.put(commentLength, ONE);
			context.write(outHour, outCommentLength);		
		}	
	}
	
	public static class MyReducer extends Reducer<IntWritable, SortedMapWritable<IntWritable, LongWritable>, IntWritable, MedianStdDevTuple>
	{
		private MedianStdDevTuple result = new MedianStdDevTuple();
		private TreeMap<Integer, Long> commentLengthCounts = new TreeMap<Integer, Long>();
		
		
		protected void reduce(IntWritable key, Iterable<SortedMapWritable<IntWritable, LongWritable>> values, 
				Context context) throws IOException ,InterruptedException 
		{
			float sum = 0;
			long totalComments = 0;
			commentLengthCounts.clear();
			result.setMedian(0);
			result.setStdDev(0);
			
			for(SortedMapWritable<IntWritable, LongWritable> v : values)
			{
				for(Entry<IntWritable, LongWritable> entry : v.entrySet())
				{
					int length = (entry.getKey()).get();
					long count = (entry.getValue()).get();
					
					totalComments += count;
					sum += length * count;
					
					Long storedCount = commentLengthCounts.get(length);
					if(null == storedCount)
					{
						commentLengthCounts.put(length, count);
					}
					else
					{
						commentLengthCounts.put(length, storedCount + count);
					}
				}
			}
			
			long medianIndex = totalComments / 2L;
			long previousComments = 0;
			long comments = 0;
			int prevKey = 0;
			for(Entry<Integer, Long> entry : commentLengthCounts.entrySet())
			{
				comments = previousComments + entry.getValue();
				if(previousComments <= medianIndex && medianIndex < comments)
				{
					if(totalComments % 2 == 0 && previousComments == medianIndex)
					{
						result.setMedian((float)(entry.getKey()+prevKey)/2.0f);
					}
					else
					{
						result.setMedian(entry.getKey());
					}
					break;
				}
				previousComments = comments;
				prevKey = entry.getKey();
			}
			
			// 计算标准差
			float mean = sum / totalComments;
			float sumOfSquares = 0.0f;
			for(Entry<Integer, Long> entry : commentLengthCounts.entrySet())
			{
				sumOfSquares += (entry.getKey() - mean) * (entry.getKey() - mean) * entry.getValue();
			}
			result.setStdDev((float)Math.sqrt(sumOfSquares / (totalComments - 1)));
			context.write(key, result);	
		}
	}
	
	public static class MyCombiner extends Reducer<IntWritable, SortedMapWritable<IntWritable, LongWritable>,
		IntWritable, SortedMapWritable<IntWritable, LongWritable>>
	{
		@Override
		protected void reduce(IntWritable key,
				Iterable<SortedMapWritable<IntWritable, LongWritable>> values,
				Context context)
				throws IOException, InterruptedException
		{

			SortedMapWritable<IntWritable, LongWritable> outValue = new SortedMapWritable<IntWritable, LongWritable>();
			
			for(SortedMapWritable<IntWritable, LongWritable> v : values)
			{
				for(Entry<IntWritable, LongWritable> entry : v.entrySet())
				{
					LongWritable count = outValue.get(entry.getKey());
					
					if(null != count)
					{
						count.set(count.get() + entry.getValue().get());
						outValue.put(entry.getKey(), count);
					}
					else
					{
						outValue.put(entry.getKey(), new LongWritable((entry.getValue()).get()));
					}
				}
			}
			context.write(key, outValue);
		}
	}


	/**
	 * @param args 文件输入输出路径
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception
	{
		Configuration conf = new Configuration();
		Job job = Job.getInstance(conf, "MedianStdDev");
		
		job.setMapperClass(MyMapper.class);
		job.setCombinerClass(MyCombiner.class);
		job.setReducerClass(MyReducer.class);
		job.setOutputKeyClass(IntWritable.class);
		job.setOutputValueClass(MedianStdDevTuple.class);
		
		job.setInputFormatClass(TextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));

		System.exit(job.waitForCompletion(true)?0:1);
	}

}
