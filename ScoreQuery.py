# coding:utf-8
# VERSION-0.3
# Date: 2017-6-2
__author__ = 'Wen Chao'
import urllib
import urllib2
from bs4 import BeautifulSoup
import re
import os


class SCORE:
	def __init__(self):
		self.url = 'http://211.70.149.134:8080/stud_score/brow_stud_score.aspx'

	# 获得打开URL就看到的网页源代码
	def getPageCodeOfInit(self):
		response = urllib2.urlopen(self.url)
		return response.read()

	# 传入姓名和身份证号码,获得所有成绩的页面代码
	def getPageCodeOfAllScores(self, StuId, Id):
		pageCode = self.getPageCodeOfInit()
		soup = BeautifulSoup(pageCode, "html.parser")
		eventvalidation = soup.find_all(id='__EVENTVALIDATION')[0].get('value')
		viewstate = soup.find_all(id='__VIEWSTATE')[0].get('value')
		postdata = urllib.urlencode({
			'TextBox1':          StuId,
			'TextBox2':          Id,
			'drop_xn':           '',
			'drop_xq':           '',
			'drop_type':         '全部成绩',
			'Button_cjcx':       '查询',
			'__EVENTVALIDATION': eventvalidation,
			'__VIEWSTATE':       viewstate
		})
		try:
			request = urllib2.Request(url=self.url, data=postdata)
			response = urllib2.urlopen(request, timeout=10)
			# 返回post数据之后的网页源代码
			return response.read()
		except urllib2.HTTPError, e:
			print e.code
			print e.reason
			return None

	# 获得学号姓名互转的页面代码
	def getPageCodeOfConverting(self):
		pageCode = self.getPageCodeOfInit()
		soup = BeautifulSoup(pageCode, "html.parser")
		post_data = urllib.urlencode({'TextBox1':          '',
		                              'TextBox2':          '',
		                              '__VIEWSTATE':       soup.find('input', id='__VIEWSTATE')['value'],
		                              # '__VIEWSTATEGENERATOR': soup.find('input', id='__VIEWSTATEGENERATOR')['value'],
		                              '__EVENTVALIDATION': soup.find('input', id='__EVENTVALIDATION')['value'],
		                              'drop_xn':           '',
		                              'drop_xq':           '',
		                              'drop_type':         '全部成绩',
		                              'btn_xhxm':          '学号姓名转换',
		                              'hid_dqszj':         ''
		                              })
		try:
			request = urllib2.Request(self.url, post_data)
			response = urllib2.urlopen(request, timeout=10)
			pageCode = response.read()
			return pageCode
		except urllib2.HTTPError, e:
			print e.code
			print e.reason
			return None

	# 获得post姓名或学号的页面代码
	def getPageCodeOfPostingNameOrId(self, NameOrId):
		pageCode = self.getPageCodeOfConverting()
		soup = BeautifulSoup(pageCode, "html.parser")
		if NameOrId.isdigit():
			post_data = urllib.urlencode({
				'TextBox1':          '',
				'TextBox2':          '',
				'TextBox3':          '',
				'TextBox4':          NameOrId,  # 姓名
				'__VIEWSTATE':       soup.find('input', id='__VIEWSTATE')['value'],
				# '__VIEWSTATEGENERATOR': soup.find('input', id='__VIEWSTATEGENERATOR')['value'],
				'__EVENTVALIDATION': soup.find('input', id='__EVENTVALIDATION')['value'],
				'drop_xn':           '',
				'drop_xq':           '',
				'drop_type':         '全部成绩',
				'Button2':           '查询',
				'hid_dqszj':         ''
			})
		else:
			post_data = urllib.urlencode({
				'TextBox1':             '',
				'TextBox2':             '',
				'TextBox3':             NameOrId,  # 学号
				'TextBox4':             '',
				'__VIEWSTATE':          soup.find('input', id='__VIEWSTATE')['value'],
				'__VIEWSTATEGENERATOR': soup.find('input', id='__VIEWSTATEGENERATOR')['value'],
				'__EVENTVALIDATION':    soup.find('input', id='__EVENTVALIDATION')['value'],
				'drop_xn':              '',
				'drop_xq':              '',
				'drop_type':            '全部成绩',
				'Button3':              '查询',
				'hid_dqszj':            ''
			})
		try:
			request = urllib2.Request(self.url, post_data)
			response = urllib2.urlopen(request, timeout=10)
			pageCode = response.read()
			return pageCode
		except urllib2.HTTPError, e:
			print e.code, ' ', e.reason
			return None

	# 获得所有学生的成绩
	def printAllScores(self, StuId, Id):
		pageCode = self.getPageCodeOfAllScores(StuId, Id)
		soup = BeautifulSoup(pageCode, "html.parser")
		p = re.compile('共找到(.*?)条', re.S)
		item = re.findall(p, pageCode)
		if len(item) == 0:
			# 如果numberOfRecord为,那么成绩记录为0或者获取页面失败
			print '没有记录或身份证号错误!'
			return None
		# '学年', '学期', '课程号', '课程名', '学分', '课程属性', '教师号', '教师姓名', '折算成绩',序号分别从0~8
		numberOfRecord = int(item[0])
		print '\n%30s%20s%20s' % ('课程名', '学分', '成绩')
		pattern = re.compile(
				'onmouseout.*?size="3">(.*?)</font>.*?size="3">(.*?)</font>.*?size="3">(.*?)</font>.*?size="3">(.*?)</font>.*?size="3">(.*?)</font>.*?size="3">(.*?)</font>.*?size="3">(.*?)</font>.*?size="3">(.*?)</font>.*?size="3">(.*?)</font>',
				re.S)
		items = re.findall(pattern, pageCode)
		# num是第0条成绩一直到第numOfRecord-1条成绩的信息
		TermUp = ''
		sumScore, sumPoint = 0.0, 0.0
		# list存储学年学期,sum(学分*成绩),sum(学分)
		list = []
		for i in range(numberOfRecord):
			TermDown = self.getTerm(items[i][0], items[i][1])
			if i == 0:
				print '==========================', TermDown, '============================='
				if items[0][5] == '必修课' or items[0][5] == '任选课':
					sumScore += float(items[0][4]) * float(items[0][8])
					sumPoint += float(items[0][4])
				TermUp = TermDown

			elif TermUp == TermDown:
				# 本条和上一条相同,学分绩求和
				if items[i][5] == '必修课' or items[i][5] == '任选课':
					sumScore += float(items[i][4]) * float(items[i][8])
					sumPoint += float(items[i][4])
				TermUp = TermDown
				# 如果是最后一条成绩信息
				if i == numberOfRecord - 1:
					list.append([TermUp, sumScore, sumPoint])

			else:
				print '==========================', TermDown, '============================='
				list.append([TermUp, sumScore, sumPoint])
				sumScore, sumPoint = 0, 0
				if items[i][5] == '必修课' or items[i][5] == '任选课':
					sumScore += float(items[i][4]) * float(items[i][8])
					sumPoint += float(items[i][4])
				TermUp = TermDown

			print ("%30s%20s%20s") % (items[i][3], items[i][4], items[i][8])
		# 打印各个学期的学分绩
		for i in list:
			print '\n============', i[0], '平均学分绩:', i[1] / i[2], '================'
		return list

	def getAveragePoint(self, list):
		score = [0, 0, 0, 0]
		for i in range(8):
			if len(list) < 8:
				list.append(['null', 0, 0])
		for i in range(4):
			score[i] = (list[i * 2][1] + list[i * 2 + 1][1]) / (list[i * 2][2] + list[i * 2 + 1][2] + 0.001)
		return score

	# 第x学年第x学期,item[i][0],item[i][1]
	def getTerm(self, XueNian, XueQi):
		return XueNian + '学年' + '第' + XueQi + '学期'

	# 通过学号获得平均学分绩,主要被getStuInfo调用
	def getAveScore(self, StuID):
		soup = BeautifulSoup(self.getPageCodeOfInit(), "html.parser")
		post_data = urllib.urlencode({'TextBox1':          StuID,
		                              'TextBox2':          '',
		                              '__VIEWSTATE':       soup.find('input', id='__VIEWSTATE')['value'],
		                              # '__VIEWSTATEGENERATOR': soup.find('input', id='__VIEWSTATEGENERATOR')['value'],
		                              '__EVENTVALIDATION': soup.find('input', id='__EVENTVALIDATION')['value'],
		                              'drop_xn':           '',
		                              'drop_xq':           '',
		                              'drop_type':         '全部成绩',
		                              'Button_xfj':        '第一专业平均学分绩',
		                              'hid_dqszj':         '',
		                              }
		                             )
		try:
			response = urllib2.urlopen(self.url, post_data, timeout=10)
		except urllib2.URLError, e:
			print e.reason
		pattern = re.compile('Label20.*?#0000FF">(.*?)</span>.*?Label21.*?#0000FF">(.*?)</span>', re.S)
		items = re.findall(pattern, response.read())
		if items == None or items[0][1] == '0':
			return None
		else:
			return float(items[0][0]) / float(items[0][1])

	def printAveScore(self, score):
		print "============================================================================"
		print "============================================================================"
		print "============ 以下是學年平均學分績, 決定了你最終能否拿到獎學金 ================"
		print "============================================================================"
		for i in range(len(score)):
			if score[i] != 0:
				print "第" + str(i + 1) + "學年平均學分績: " + str(score[i])

	# 返回查询到的所有学生的信息
	def getStuInfo(self, NameOrId):
		pageCode = self.getPageCodeOfPostingNameOrId(NameOrId)
		soup = BeautifulSoup(pageCode, "html.parser")
		# 正则匹配,提取个人信息
		pattern = re.compile(
				'Black">(.*?)</font>.*?Black">(.*?)</font>.*?Black">(.*?)</font>.*?Black">(.*?)</font>.*?Black">(.*?)</font>.*?Black">(.*?)</font>.*?Black">(.*?)</font>',
				re.S)
		items = re.findall(pattern, pageCode)
		return items

	def printStuInfo(self, NameOrId):
		items = self.getStuInfo(NameOrId)
		print '=============================共', len(items), '条符合条件!================================\n'
		if len(items) == 0:
			print '查无此项!'

		elif len(items) == 1:
			print '学号:', items[0][0], '\t', '姓名:', items[0][1], '\t', '性别:', items[0][2], '\t', '学院:', \
				items[0][3], '\t', '专业:', items[0][4], '\t', '班级:', items[0][5], \
				'\n平均学分绩:', self.getAveScore(items[0][0])
			print '==============================================================================='

		elif len(items) <= 100:
			for item in items:
				print '学号:', item[0], '\t', '姓名:', item[1], '\t', \
					'性别:', item[2], '\t\t', '学院:', item[3], '\t', \
					'专业:', item[4], '\t', '班级:', item[5]
				print '平均学分绩:', self.getAveScore(item[0])
				print '==============================================================================='
		else:
			print '=======================请求过多,最多将为您显示100条信息!=======================\n'
			times = 100
			# items一个大list,里面每一个元素是一个小list,每个小list包含学号,姓名等信息
			for item in items:
				times -= 1
				print '学号:', item[0], '\t', '姓名:', item[1], '\t', \
					'性别:', item[2], '\t', '学院:', item[3], '\t', \
					'专业:', item[4], '\t', '班级:', item[5]
				print '平均学分绩:', self.getAveScore(item[0])
				print '==============================================================================='
				if times <= 0:
					break

	def convertNameToId(self, NameOrId):
		items = self.getStuInfo(NameOrId)
		return items[0][0]

	def printHelp(self):
		print """
        输入姓名或学号的关键字，即可查询Ta的个人信息.
        
        例如：您姓‘李’，那么输入‘李’即可查询所有姓李的同学的信息.
        
        再如：输入14907即可查询安工大所有14级计算机学院学生的信息.
        
        如果您发现任何问题，或者有更好的建议，欢迎与本人取得联系!

        """

	def start(self, NameOrId):
		# 输出帮助
		if NameOrId == 'h':
			self.printHelp()
			NameOrId = raw_input('请输入姓名或学号(q退出,h帮助):')
			self.start(NameOrId)
		# 退出，同时输出版权信息
		elif NameOrId == 'q':
			self.exit()
		# 输出学生信息
		else:
			self.printStuInfo(NameOrId)
			Id = raw_input("查看所有成绩,请输入身份证号(q退出):")
			if Id == 'q':
				self.exit()
			else:
				StuId = self.convertNameToId(NameOrId)
				list = self.printAllScores(StuId, Id)
				self.printAveScore(self.getAveragePoint(list))
				print '\n'

				NameOrId = raw_input('请输入姓名或学号(q退出,h帮助):')
				self.start(NameOrId)

	def exit(self):
		print """
        AHTHOR:
            Written by Aaron Wen.
            
        REPORTING BUGS:
            Report bugs to aaron.csie@gmail.com
            
        ABOUT:
            Score Query System of AHUT
            Current Version: 0.3
            Release date: 2017-6-2
             """


ahut = SCORE()
NameOrId = raw_input('请输入姓名或学号(q退出,h帮助):')
ahut.start(NameOrId)
