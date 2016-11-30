package com.cnblogs.vincentzh.hadooptest;

import org.apache.hadoop.io.Writable;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.Partitioner;
import org.apache.hadoop.yarn.state.Graph.Edge;

public class EdgePartitioner implements Partitioner<Edge, Writable>
{
	public int getPartition(Edge key, Writable value, int numberPartitions)
	{
		return key.hashCode() % numberPartitions;
	}

	@Override
	public void configure(JobConf jobConf)
	{		
		
	};
}
