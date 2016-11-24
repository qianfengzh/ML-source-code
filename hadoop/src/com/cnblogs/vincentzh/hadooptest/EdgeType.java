package com.cnblogs.vincentzh.hadooptest;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

import org.apache.hadoop.io.WritableComparable;

public class EdgeType implements WritableComparable<EdgeType>
{

	private String depatureNode;
	private String arrivalNode;
	
	@Override
	public void readFields(DataInput in) throws IOException
	{
		depatureNode = in.readUTF();
		arrivalNode = in.readUTF();
		
	}

	@Override
	public void write(DataOutput out) throws IOException
	{
		out.writeUTF(depatureNode);
		out.writeUTF(arrivalNode);
		
	}

	@Override
	public int compareTo(EdgeType o)
	{
		return (depatureNode.compareTo(o.depatureNode) !=0)?
				depatureNode.compareTo(o.depatureNode):
					arrivalNode.compareTo(o.arrivalNode);
	}

}
