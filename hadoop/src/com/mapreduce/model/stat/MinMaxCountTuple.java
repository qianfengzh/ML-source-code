package com.mapreduce.model.stat;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

import org.apache.hadoop.io.Writable;

// 自定义数据存储格式
public class MinMaxCountTuple implements Writable
{
	private Date min = new Date(); // 用户第一次评论时间
	private Date max = new Date(); // 用户最后一次评论时间
	private long count = 0; // 该用户所有的评论数
	
	private final static SimpleDateFormat frmt = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS");

	public Date getMin()
	{
		return min;
	}

	public void setMin(Date min)
	{
		this.min = min;
	}

	public Date getMax()
	{
		return max;
	}

	public void setMax(Date max)
	{
		this.max = max;
	}

	public long getCount()
	{
		return count;
	}

	public void setCount(long count)
	{
		this.count = count;
	}

	@Override
	public void readFields(DataInput in) throws IOException
	{
		// Read the data in in the order it is written,
		// creating new Date objects from the UNIX timestamp
		min = new Date(in.readLong());
		max = new Date(in.readLong());
		count = in.readLong();
	}

	@Override
	public void write(DataOutput out) throws IOException
	{
		// Write the data out in the order it is read,
		out.writeLong(min.getTime());
		out.writeLong(max.getTime());
		out.writeLong(count);
	}
	
	public String toString()
	{
		return frmt.format(min) + "\t" + frmt.format(max) + "\t" + count;
	}
}














