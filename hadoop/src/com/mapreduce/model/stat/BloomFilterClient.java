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

// ��¡�����������˳� hot values
// Ԥ��ȷ���Ĵʼ��β���һ����¡���������������Ϊһ��gzip�����ļ�
// ��һ�� gzip �ļ�Ŀ¼���ļ��е�Ԫ����Ŀ��һ�������̵������ʡ�
// ��������ļ���
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
		
		// ����������С�����ڸ����Ż� k ֵ
		int vectorSize = getOptimalBloomFilterSize(numMembers, falsePosRate);
		int nbHash = getOptimalK(numMembers, vectorSize);
		
		// �����µĲ�¡������
		BloomFilter filter = new BloomFilter(vectorSize, nbHash, Hash.MURMUR_HASH);
		
		System.out.println("Training Bloom filter of size" + vectorSize
				+ "with" + nbHash + "hash functions," + numMembers
				+ "approximate number of records, and" + falsePosRate
				+ "false positive rate");
		
		// ���ļ���ȡ
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
