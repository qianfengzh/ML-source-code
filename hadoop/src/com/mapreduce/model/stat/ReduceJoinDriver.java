package com.mapreduce.model.stat;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.MultipleInputs;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

// 给定一个用户信息几何和一个用户评论列表，通过为每一条评论添加创建
// 该评论的用户信息来丰富评论的内容。

// 连接是在 reducer 端进行的，所有 combiner 将不会对优化有太大帮助

public class ReduceJoinDriver
{
	public static class UserJoinMapper extends Mapper<Object, Text, Text, Text>
	{
		private Text outkey = new Text();
		private Text outvalue = new Text();
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			String userId = parsed.get("Id");
			
			outkey.set(userId);
			outvalue.set("A" + value.toString());
			context.write(outkey, outvalue);
		}
	}
	
	public static class CommentJoinMapper extends Mapper<Object, Text, Text, Text>
	{
		private Text outkey = new Text();
		private Text outvalue = new Text();
		
		@Override
		protected void map(Object key, Text value,
				Context context)
				throws IOException, InterruptedException
		{
			Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
			
			outkey.set(parsed.get("UserId"));
			outvalue.set("B" + value.toString());
			context.write(outkey, outvalue);
		}
	}
	
	
	public static class UserJoinReducer extends Reducer<Text, Text, Text, Text>
	{
		private static final Text EMPTY_TEXT = new Text("");
		private Text tmp = new Text();
		private ArrayList<Text> listA = new ArrayList<Text>();
		private ArrayList<Text> listB = new ArrayList<Text>();
		private String joinType = null;
		
		@Override
		protected void setup(Context context)
				throws IOException, InterruptedException
		{
			joinType = context.getConfiguration().get("join.type");
		}
		
		@Override
		protected void reduce(Text key, Iterable<Text> values,
				Context context)
				throws IOException, InterruptedException
		{
			listA.clear();
			listB.clear();
			
			for (Text value:values)
			{
				tmp = value;
				if (tmp.charAt(0) == 'A')
				{
					listA.add(new Text(tmp.toString().substring(1)));
				}
				else if (tmp.charAt(0) == 'B')
				{
					listB.add(new Text(tmp.toString().substring(1)));
				}
			}
			
			executeJoinLogic(context);
		}
		
		private void executeJoinLogic(Context context) throws IOException, InterruptedException
		{
			if (joinType.equalsIgnoreCase("inner"))
			{
				if (!listA.isEmpty() && !listB.isEmpty())
				{
					for (Text A : listA)
					{
						for (Text B : listB)
						{
							context.write(A, B);
						}
					}
				}
			}
			else if (joinType.equalsIgnoreCase("leftouter"))
			{
				for (Text A : listA)
				{
					if (!listB.isEmpty())
					{
						for (Text B : listB)
						{
							context.write(A, B);
						}
					}
					else
					{
						context.write(A, EMPTY_TEXT);
					}
				}
			}
			else if (joinType.equalsIgnoreCase("rightouter"))
			{
				for (Text B : listB)
				{
					if (!listA.isEmpty())
					{
						for (Text A : listA)
						{
							context.write(A, B);
						}
					}
					else
					{
						context.write(EMPTY_TEXT, B);
					}
				}
			}
			else if (joinType.equalsIgnoreCase("fullouter"))
			{
				if (!listA.isEmpty())
				{
					for (Text A : listA)
					{
						if (!listB.isEmpty())
						{
							for (Text B : listB)
							{
								context.write(A, B);
							}
						}
						else
						{
							context.write(A, EMPTY_TEXT);
						}
					}
				}
				else
				{
					for (Text B : listB)
					{
						if (!listA.isEmpty())
						{
							for (Text A : listA)
							{
								context.write(A, B);
							}
						}
						else
						{
							context.write(EMPTY_TEXT, B);
						}
					}
				}
			}
			else if (joinType.equalsIgnoreCase("anti"))
			{
				if (listA.isEmpty() ^ listB.isEmpty())
				{
					for (Text A : listA)
					{
						context.write(A, EMPTY_TEXT);
					}
					for (Text B : listB)
					{
						context.write(EMPTY_TEXT, B);
					}
				}
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
		Job job = Job.getInstance(conf, "ReduceJoin");
		
		job.setJarByClass(ReduceJoinDriver.class);
		//job.setMapperClass(UserJoinMapper.class);
		job.setMapperClass(CommentJoinMapper.class);
		job.setReducerClass(UserJoinReducer.class);
		
		//job.setInputFormatClass(TextInputFormat.class);
		job.setOutputFormatClass(TextOutputFormat.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(Text.class);
		
		MultipleInputs.addInputPath(job, new Path(args[0]), TextInputFormat.class, UserJoinMapper.class);
		MultipleInputs.addInputPath(job, new Path(args[1]), TextInputFormat.class, CommentJoinMapper.class);
		FileOutputFormat.setOutputPath(job, new Path(args[2]));
		job.getConfiguration().set("join.type", args[3]);
		
		System.exit(job.waitForCompletion(true) ? 0 : 1);
		
	}

}
