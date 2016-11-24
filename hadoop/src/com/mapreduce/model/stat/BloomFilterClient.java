package com.mapreduce.model.stat;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.zip.GZIPInputStream;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.util.bloom.BloomFilter;
import org.apache.hadoop.util.bloom.Key;
import org.apache.hadoop.util.hash.Hash;

// 布隆过滤器，过滤出 hot values
// 预先确定的词几何产生一个布隆过滤器，输入参数为一个gzip输入文件
// 或一个 gzip 文件目录、文件中的元素数目、一个可容忍的误判率、
// 及输出的文件名
public class BloomFilterClient
{

	/**
	 * @param args
	 */
	public static void main(String[] args)
	{
		Path inputFile = new Path(args[0]);
		int numMembers = Integer.parseInt(args[1]);
		float falsePosRate = Float.parseFloat(args[2]);
		Path bfFile = new Path(args[3]);
		
		// 计算向量大小并基于概率优化 k 值
		int vectorSize = getOptimalBloomFilterSize(numMembers, falsePosRate);
		int nbHash = getOptimalK(numMembers, vectorSize);
		
		// 创建新的布隆过滤器
		BloomFilter filter = new BloomFilter(vectorSize, nbHash, Hash.MURMUR_HASH);
		
		System.out.println("Training Bloom filter of size" + vectorSize
				+ "with" + nbHash + "hash functions," + numMembers
				+ "approximate number of records, and" + falsePosRate
				+ "false positive rate");
		
		// 打开文件读取
		String line = null;
		int numElements = 0;
		FileSystem fs = FileSystem.get(new Configuration());
		
		for (FileStatus status : fs.listStatus(inputFile))
		{
			BufferedReader rdr = new BufferedReader(new InputStreamReader(new GZIPInputStream(fs.open(status.getPath()))));
			System.out.println("Reading" + status.getPath());
			
			while((line = rdr.readLine()) != null)
			{
				filter.add(new Key(line.getBytes()));
				++numElements;
			}
			
			rdr.close();
		}
		System.out.println("Trained Bloom filter with" + numElements + "entries.");
		System.out.println("Serializing Bloom filter to HDFS at" + bfFile);
		
		FSDataOutputStream strm = fs.create(bfFile);
		filter.write(strm);
		strm.flush();
		strm.close();
		
		System.exit(0);	
		
	}

}
