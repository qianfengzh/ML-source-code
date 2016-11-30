package com.mapreduce.model.stat;
// 给定一个用户列表，过滤屌声望值小于1500的用户发出的评论
import java.io.DataInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.net.URI;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.shell.CopyCommands.Get;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.filecache.DistributedCache;
import org.apache.hadoop.util.bloom.BloomFilter;
import org.apache.hadoop.util.bloom.Key;

import com.sun.corba.se.spi.orbutil.fsm.Guard.Result;

public class HBaseBloomFilterMapper extends 
				Mapper<Object, Text, Text, NullWritable>
{
	private BloomFilter filter = new BloomFilter();
	private HTable table = null;

	@Override
	protected void setup(Context context)
			throws IOException, InterruptedException
	{
		URI[] files = DistributedCache.getCacheFiles(context.getConfiguration());
		System.out.println("Reading Bloom filter from:" + files[0].getPath());
		
		DataInputStream strm = new DataInputStream(new FileInputStream(files[0].getPath()));
		filter.readFields(strm);
		strm.close();
		
		Configuration hconf = HBaseConfiguration.create();
		table = new HTable(hconf, "user_table");
	}
	
	@Override
	public void map(Object key, Text value, Context context)
			throws IOException, InterruptedException
	{
		Map<String, String> parsed = MRDPUtils.transformXmlToMap(value.toString());
		
		String userid = parsed.get("UserId");
		
		if(filter.membershipTest(new Key(userid.getBytes())))
		{
			Result r = table.get(new Get(userid.getBytes()));
			int reputation = Integer.parseInt(new String(r.getValue("attr".getBytes(), "Reputation".getBytes())))；
			if(reputation >= 1500)
			{
				context.write(value, NullWritable.get());
			}
		}
	
	}

}
