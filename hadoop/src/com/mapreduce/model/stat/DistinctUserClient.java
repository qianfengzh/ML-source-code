package com.mapreduce.model.stat;

import java.io.IOException;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

// 给定一个用户评论列表，得到去重的用户ID集


// 通过partitioner将数据分发到各个reducer,所有的去重工作全部都在reducer中进行
// 使用框架自身的特性，reducer端的输入是key与value集，即一个value集公用一个key,
// 那么直接拿到value集对应的key即可。

// 同样的reducer端代码可直接用于combiner的优化

public class DistinctUserClient
{
	public static class DistinctUserMapper extends Mapper<Object, Text, Text, NullWritable>
	{
		private Text outUserId = new Text();
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			String userId = parsed.get("UserId");
			outUserId.set(userId);
			context.write(outUserId, NullWritable.get());
		}
	}
	
	
	// 使用框架自身的特性，reducer的key/value(集)输入值特性
	public static class DistinctUserReducer extends Reducer<Text, NullWritable, Text, NullWritable>
	{
		@Override
		protected void reduce(Text key, Iterable<NullWritable> values,
				Context context)
				throws IOException, InterruptedException
		{
			context.write(key, NullWritable.get());
		}
	}
	
	
	/**
	 * @param args
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception
	{
		Configuration conf = new Configuration();
		Job job = Job.getInstance(conf, "DistinctUser");
		
		job.setMapperClass(DistinctUserMapper.class);
		job.setReducerClass(DistinctUserReducer.class);
		job.setInputFormatClass(TextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(NullWritable.class);
		
		FileInputFormat.addInputPath(job, new Path(args[0]));
		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		
		System.exit(job.waitForCompletion(true) ? 0 :1);
	}

}
