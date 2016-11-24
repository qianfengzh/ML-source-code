package com.mapreduce.model.stat;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

import org.apache.hadoop.io.Writable;

public class MedianStdDevTuple implements Writable
{
	private float median;
	private float stdDev;
	
	public float getMedian()
	{
		return median;
	}

	public void setMedian(float median)
	{
		this.median = median;
	}

	public float getStdDev()
	{
		return stdDev;
	}

	public void setStdDev(float stdDev)
	{
		this.stdDev = stdDev;
	}

	@Override
	public void readFields(DataInput in) throws IOException
	{
		this.median = in.readFloat();
		this.stdDev = in.readFloat();
	}
	
	@Override
	public void write(DataOutput out) throws IOException
	{
		out.writeFloat(median);
		out.writeFloat(stdDev);
	}

	@Override
	public String toString()
	{
		return median + "\t" + stdDev;
	}

}
