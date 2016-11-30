package com.cnblogs.vincentzh.hadooptest;

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.LocalFileSystem;
import org.apache.hadoop.fs.Path;

public class MergeFile
{
	/**
	 * @param args
	 * @throws IOException 
	 */
	public static void main(String[] args) throws IOException
	{
		Configuration conf = new Configuration();
		FileSystem hdfs = FileSystem.get(conf);
		LocalFileSystem local = FileSystem.getLocal(conf);
		
		Path inputPath = new Path("H:/mergeFile");
		Path outputPath = new Path("hdfs://192.168.1.110:9000/user/hadoop/mergedFile");
		
		FileStatus[] inputFile = local.listStatus(inputPath); // 被合并的路径总是要通过 FileStatus 来间接处理多个文件
		FSDataOutputStream out = hdfs.create(outputPath); // 合并的目的路径只需 create 出来即可
		//当反向处理时（hdfs 合并到 local），恰好相反，hdsf 上需要间接处理路径，
		//而local 直接处理即可，因为 LocalFileSystem 是从 FileSystem 继承下来的。
		
		for (int i=0; i < inputFile.length; i++)
		{
			System.out.println(inputFile[i].getPath().getName());
		
		FSDataInputStream in = local.open(inputFile[i].getPath());
		byte[] buffer = new byte[256];
		int byteRead = 0;
		while((byteRead = in.read(buffer))>0) // in 能读 byte 类型是因为 FSDataInputStream 继承了 InputStream 的read方法
		{
			out.write(byteRead);
		}
		in.close();
		
		}
		out.close();

	}

}
