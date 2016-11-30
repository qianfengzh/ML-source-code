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
		
		FileStatus[] inputFile = local.listStatus(inputPath); // ���ϲ���·������Ҫͨ�� FileStatus ����Ӵ������ļ�
		FSDataOutputStream out = hdfs.create(outputPath); // �ϲ���Ŀ��·��ֻ�� create ��������
		//��������ʱ��hdfs �ϲ��� local����ǡ���෴��hdsf ����Ҫ��Ӵ���·����
		//��local ֱ�Ӵ����ɣ���Ϊ LocalFileSystem �Ǵ� FileSystem �̳������ġ�
		
		for (int i=0; i < inputFile.length; i++)
		{
			System.out.println(inputFile[i].getPath().getName());
		
		FSDataInputStream in = local.open(inputFile[i].getPath());
		byte[] buffer = new byte[256];
		int byteRead = 0;
		while((byteRead = in.read(buffer))>0) // in �ܶ� byte ��������Ϊ FSDataInputStream �̳��� InputStream ��read����
		{
			out.write(byteRead);
		}
		in.close();
		
		}
		out.close();

	}

}
