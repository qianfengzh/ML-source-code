package com.mapreduce.model.stat;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Map;

import org.apache.hadoop.conf.Configurable;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Partitioner;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

// 给定一组用户信息，按照最近访问日期中的年份信息对记录进行分区，
// 一年对应一个分区。

public class LastAccessDataDriver
{
	public static class LastAccessDataMapper extends Mapper<Object, Text, IntWritable, Text>
	{
		private final static SimpleDateFormat frmt = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSS");
		
		private IntWritable outkey = new IntWritable();
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			String strDate = parsed.get("LastAccessDate");
			
			Calendar cal = Calendar.getInstance();
			try
			{
				cal.setTime(frmt.parse(strDate));
			}
			catch (ParseException e)
			{
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			outkey.set(cal.get(Calendar.YEAR));
			context.write(outkey, value);
		}
	}
	
	
	public static class LastAccessDataPartitioner extends Partitioner<IntWritable, Text> implements Configurable
	{
		private static final String MIN_LAST_ACCESS_DATE_YEAR = "min.last.access.date.year";
		private Configuration conf = null;
		private int minLastAccessDateYear = 0;
		
		private static void setMinLastAccessDate(Job job, int minLastAccessDateYear)
		{
			job.getConfiguration().setInt(MIN_LAST_ACCESS_DATE_YEAR, minLastAccessDateYear);
		}
		
		@Override
		public Configuration getConf()
		{
			return conf;
		}

		@Override
		public void setConf(Configuration conf)
		{
			this.conf = conf;
			minLastAccessDateYear = conf.getInt(MIN_LAST_ACCESS_DATE_YEAR, 0);
		}

		@Override
		public int getPartition(IntWritable key, Text value, int numPartitions)
		{
			return key.get() - minLastAccessDateYear;
		}
	}
	
	
	
	public static class ValueReducer extends Reducer<IntWritable, Text, Text, NullWritable>
	{
		@Override
		protected void reduce(IntWritable key, Iterable<Text> values,
				Context context)
				throws IOException, InterruptedException
		{
			for (Text t : values)
			{
				context.write(t, NullWritable.get());
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
		Job job = Job.getInstance(conf, "LastAccessData");
		
		job.setMapperClass(LastAccessDataMapper.class);
		job.setPartitionerClass(LastAccessDataPartitioner.class);
		job.setReducerClass(ValueReducer.class);
		LastAccessDataPartitioner.setMinLastAccessDate(job, 2008);
		job.setNumReduceTasks(4);
		
		job.setInputFormatClass(TextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(NullWritable.class);
		
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		
		System.exit(job.waitForCompletion(true) ? 0 :1);
	}

}
