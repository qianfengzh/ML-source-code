package com.mapreduce.model.stat;
// �� DistributedCache �н�ѵ���õĲ�¡�����������л�����ʹ��
import java.io.DataInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.net.URI;
import java.util.Map;
import java.util.StringTokenizer;

import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.filecache.DistributedCache;
import org.apache.hadoop.util.bloom.BloomFilter;
import org.apache.hadoop.util.bloom.Key;

public class BloomFilterMapper extends Mapper<Object, Text, Text, NullWritable>
{
	private BloomFilter filter = new BloomFilter();
	
	@Override
	protected void setup(Context context)
			throws IOException, InterruptedException
	{
		// �� DistributedCache �л�ȡ��¡������
		URI[] files = DistributedCache.getCacheFiles(context.getConfiguration());
		System.out.println("Reading Bloom filter from:" + files[0].getPath());
	
		DataInputStream strm = new DataInputStream(new FileInputStream(files[0].getPath()));
		
		filter.readFields(strm);
		strm.close();
	}
	
	
	@Override
	public void map(Object key, Text value, Context context)
			throws IOException, InterruptedException
	{
		Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
		String comment = parsed.get("Text");
		StringTokenizer tokenizer = new StringTokenizer(comment);
		
		while(tokenizer.hasMoreElements())
		{
			String word = tokenizer.nextToken();
			if(filter.membershipTest(new Key(word.getBytes())))
			{
				context.write(value, NullWritable.get());
			}
		}
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
	}

}
