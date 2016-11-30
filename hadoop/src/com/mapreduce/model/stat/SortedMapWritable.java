package com.mapreduce.model.stat;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.util.Map.Entry;
import java.util.TreeMap;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Writable;

public class SortedMapWritable<K, V> extends TreeMap<K, V> implements Writable
{
	private TreeMap<IntWritable, LongWritable> treeMap = new TreeMap<IntWritable, LongWritable>();

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	@Override
	public void readFields(DataInput in) throws IOException
	{
		treeMap.put(new IntWritable(in.readInt()), new LongWritable(in.readLong()));
	}

	@Override
	public void write(DataOutput out) throws IOException
	{
		for (Entry<IntWritable, LongWritable> entry : treeMap.entrySet())
		{
			out.writeInt(entry.getKey().get());
			out.writeLong(entry.getValue().get());
		}		
	}
}
