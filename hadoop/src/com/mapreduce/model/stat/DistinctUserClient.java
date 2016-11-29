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

// ����һ���û������б��õ�ȥ�ص��û�ID��


// ͨ��partitioner�����ݷַ�������reducer,���е�ȥ�ع���ȫ������reducer�н���
// ʹ�ÿ����������ԣ�reducer�˵�������key��value������һ��value������һ��key,
// ��ôֱ���õ�value����Ӧ��key���ɡ�

// ͬ����reducer�˴����ֱ������combiner���Ż�

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
	
	
	// ʹ�ÿ����������ԣ�reducer��key/value(��)����ֵ����
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
