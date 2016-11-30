package com.cnblogs.vincentzh.hadooptest;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.Writable;
import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileSplit;
import org.apache.hadoop.mapred.InputSplit;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.RecordReader;
import org.apache.hadoop.mapred.Reporter;


public class TimeUrlTextInputFormat extends FileInputFormat<Text, URLWritable>
{
	@Override
	public RecordReader<Text, URLWritable> getRecordReader(
			InputSplit input, JobConf job, Reporter reporter) throws IOException
	{
		return new TimeUrlLineRecordReader(job, (FileSplit)input);
	}

}


class URLWritable implements Writable
{
	private URL url;

	public URLWritable(){};
	public URLWritable(URL url)
	{
		this.url = url;
	}
	
	
	@Override
	public void readFields(DataInput in) throws IOException
	{
		url = new URL(in.readUTF());
		
	}

	@Override
	public void write(DataOutput out) throws IOException
	{
		out.writeUTF(url.toString());			
	}	
	
	public void set(Text val) throws MalformedURLException
	{
		url = new URL(val.toString());
	}
}

