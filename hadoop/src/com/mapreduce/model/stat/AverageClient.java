package com.mapreduce.model.stat;

// 按天计算每小时的平均评论长度

// XML数据结构
/* <row Id="8189677" PostId="6881722" Text="Have you looked at
 * Hadoop? CreationDate="2011-07-30T07:29:33.343" UserId="831878"/>
 *
 */
import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

public class AverageClient
{
	public static class AverageMapper extends Mapper<Object, Text, IntWritable, CountAverageTuple>
	{
		private IntWritable outHour = new IntWritable();
		private CountAverageTuple outCountAverage = new CountAverageTuple();
		private final static SimpleDateFormat frmt = new SimpleDateFormat(
				"yyyy-MM-dd'T'HH:mm:ss.SSSS");
		private Date creationDate;
		
		@SuppressWarnings("deprecation")
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			// 获取先相关元素
			String strDate = parsed.get("CreationDate");
			String text = parsed.get("Text");
			
			// 生成输出
			try
			{
				creationDate = frmt.parse(strDate);
			}
			catch (ParseException e)
			{
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			outHour.set(creationDate.getHours());
			
			outCountAverage.setCount(1);
			outCountAverage.setAverage(text.length());
			
			context.write(outHour, outCountAverage);
		}
	}		
		
		public static class AverageReduce extends Reducer<IntWritable, CountAverageTuple, IntWritable, CountAverageTuple>
		{
			private CountAverageTuple result = new CountAverageTuple();
			
			@Override
			protected void reduce(IntWritable key,
					Iterable<CountAverageTuple> values,Context context)
					throws IOException, InterruptedException
			{
				float sum = 0;
				float count = 0;
				for (CountAverageTuple val : values)
				{
					sum += val.getCount() * val.getAverage();
					count += val.getCount();
				}
				
				result.setCount(count);
				result.setAverage(sum);
				
				context.write(key, result);
			}
		}

	
	public static void main(String[] args) throws Exception
	{
		Configuration conf = new Configuration();
		Job job = Job.getInstance(conf, "Average");
		
		job.setJar("AverageClient");
		job.setMapperClass(AverageMapper.class);
		job.setCombinerClass(AverageReduce.class);
		job.setReducerClass(AverageReduce.class);
		job.setInputFormatClass(TextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(IntWritable.class);
		job.setOutputValueClass(CountAverageTuple.class);
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		
		System.exit(job.waitForCompletion(true)?0:1);
	}
}
