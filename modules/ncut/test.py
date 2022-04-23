#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pandas as pd
import re


# site = 'ncut.edu.cn'
# # url = 'http://cic.ncut.edu.cn/../../index.htm'
# url = 'http://cic.ncut.edu.cn/content.jsp/../../zyzx.jsp?urltype=tree.TreeTempUrl&wbtreeid=1007'
#
# while '/../' in url:
#     while re.search(r'%s/\.\./' % site, url):
#         url = re.sub(r'%s/\.\.' % site, site, url)
#     url = re.sub(r'[^/]+/\.\./', '', url)
#
# print(url)

# df = pd.read_csv('latest\\nuct_urls.2022032702.csv')
#
# with pd.ExcelWriter('latest\\output.xlsx') as fout:
#     df.to_excel(fout, sheet_name='all_urls')
#     df[['url_in']].groupby(['url_in'])['url_in'].\
#         count().\
#         reset_index(name='count').\
#         sort_values(['count'], ascending=False).\
#         to_excel(fout, sheet_name='url_in', index=False)
#
#     df[['domain']].groupby(['domain'])['domain']. \
#         count(). \
#         reset_index(name='count'). \
#         sort_values(['count'], ascending=False). \
#         to_excel(fout, sheet_name='domain', index=False)


s = """
ï»¿<HTML><HEAD><TITLE>Online application-North China University of Technology</TITLE><META Name="keywords" Content="North China University of Technology,Online,application" />
<META Name="description" Content="The following url isÂ NCUTÂ admission applicationÂ interface of theÂ Chinese language, undergraduate and graduate programs.https://ncut.17gz.org/member/login.do" />



<META content="text/html; charset=UTF-8" http-equiv="Content-Type">
<META content="IE=edge,chrome=1" http-equiv="X-UA-Compatible"><LINK rel="stylesheet" href="../../css/style.css"><LINK rel="stylesheet" href="../../css/media.css"><LINK rel="stylesheet" href="../../css/bdcss.css"><LINK rel="stylesheet" href="../../css/nav.css"><script type="text/javascript" src="../../js/bdtxk.js"></script><script type="text/javascript" src="../../js/menu.js"></script><script src="../../js/nav.js"></script>
<script src="../../js/jquery-migrate.min.js"></script>
<!--Announced by Visual SiteBuilder 9-->
<link rel="stylesheet" type="text/css" href="../../_sitegray/_sitegray.css" />
<script language="javascript" src="../../_sitegray/_sitegray.js"></script>
<!-- CustomerNO:77656262657232307e784750535b5742000100004056 -->
<link rel="stylesheet" type="text/css" href="../../content.vsb.css" />
<script type="text/javascript" src="/system/resource/js/vsbscreen.min.js" id="_vsbscreen" devices="pc|pad"></script>
<script type="text/javascript" src="/system/resource/js/counter.js"></script>
<script type="text/javascript">_jsq_(1008,'/content.jsp',1202,1399944793)</script>
</HEAD>
<BODY><!------top start------>
<DIV id="top1" class="top-bg w100">
<DIV class="head w96">
<DIV class="logo fl">
<!-- ç½ç«logoå¾çå°åè¯·å¨æ¬ç»ä»¶"åå®¹éç½®-ç½ç«logo"å¤å¡«å -->
<a href="../../index.htm" title="åæ¹å·¥ä¸å¤§å­¦è±æç½"><img src="../../images/logo1.png" width="916" height="85"></a></DIV>
<DIV class="head-r fr">
<DIV class="form"><script type="text/javascript">
    function _nl_ys_check(){
        
        var keyword = document.getElementById('showkeycode1029608').value;
        if(keyword==null||keyword==""){
            alert("è¯·è¾å¥ä½ è¦æ£ç´¢çåå®¹ï¼");
            return false;
        }
        if(window.toFF==1)
        {
            document.getElementById("lucenenewssearchkey1029608").value = Simplized(keyword );
        }else
        {
            document.getElementById("lucenenewssearchkey1029608").value = keyword;            
        }
        var  base64 = new Base64();
        document.getElementById("lucenenewssearchkey1029608").value = base64.encode(document.getElementById("lucenenewssearchkey1029608").value);
        new VsbFormFunc().disableAutoEnable(document.getElementById("showkeycode1029608"));
        return true;
    } 
</script>
<form action="../../ssy.jsp?wbtreeid=1008" method="post" id="au1a" name="au1a" onsubmit="return _nl_ys_check()" style="display: inline">
 <input type="hidden" id="lucenenewssearchkey1029608" name="lucenenewssearchkey" value=""><input type="hidden" id="_lucenesearchtype1029608" name="_lucenesearchtype" value="1"><input type="hidden" id="searchScope1029608" name="searchScope" value="0">
  <input name="showkeycode" id="showkeycode1029608" class="search-left fl">
         
         <input type="image" class="search-right fr" src="../../images/so-bt.png">
 
 
  
</form><script language="javascript" src="/system/resource/js/base64.js"></script><script language="javascript" src="/system/resource/js/formfunc.js"></script>
</DIV>
<DIV class="zh"><script language="javascript" src="/system/resource/js/dynclicks.js"></script><script language="javascript" src="/system/resource/js/openlink.js"></script><A href="http://www.ncut.edu.cn/">ä¸­æ</A>
</DIV></DIV></DIV>
<DIV class="nav w94"><UL class="menu">

<LI class="nav-h">
<DIV><A href="../../About/Overview.htm">About<IMG src="../../images/nav-bt.png"></A></DIV>
<UL class="submenu Blind">
<LI><A href="../../About/Overview.htm">Overview</A> </LI>
<LI><A href="../../About/Message_from_the_President.htm">Message from the President</A> </LI>
<LI><A href="../../About/Statistics___Facts.htm">Statistics &amp; Facts</A> </LI>
<LI><A href="../../About/Current_Administrators.htm">Current Administrators</A> </LI>
<LI><A href="../../About/NCUT_s_70th_Anniversary.htm">NCUT's 70th Anniversary</A> </LI>
</UL>
</LI>


<LI class="nav-h">
<DIV><A href="../../Academics1/Schools.htm">Academics<IMG src="../../images/nav-bt.png"></A></DIV>
<UL class="submenu Blind">
<LI><A href="../../Academics1/Schools.htm">Schools</A> </LI>
<LI><A href="../../Academics1/Academic_Programs.htm">Academic Programs</A> </LI>
<LI><A href="../../Academics1/Programmes_Taught_in_English.htm">Programmes Taught in English</A> </LI>
<LI><A href="../../Academics1/Research.htm">Research</A> </LI>
</UL>
</LI>


<LI class="nav-h">
<DIV><A href="../../Admissions1/Undergraduate.htm">Admissions<IMG src="../../images/nav-bt.png"></A></DIV>
<UL class="submenu Blind">
<LI><A href="../../Admissions1/Undergraduate.htm">Undergraduate</A> </LI>
<LI><A href="../../Admissions1/Graduate.htm">Graduate</A> </LI>
<LI><A href="../../Admissions1/Chinese_Language_Program.htm">Chinese Language Program</A> </LI>
<LI><A href="../../Admissions1/Tuition___Scholarship.htm">Tuition &amp; Scholarship</A> </LI>
</UL>
</LI>


<LI class="nav-h">
<DIV><A href="../../International/International_Office.htm">International<IMG src="../../images/nav-bt.png"></A></DIV>
<UL class="submenu Blind">
<LI><A href="../../International/International_Office.htm">International Office</A> </LI>
<LI><A href="../../International/International_School.htm">International School</A> </LI>
<LI><A href="../../International/Jobs.htm">Jobs</A> </LI>
</UL>
</LI>


<LI class="nav-h">
<DIV><A href="../../Campus_Life/Video_Presentation.htm">Campus Life<IMG src="../../images/nav-bt.png"></A></DIV>
<UL class="submenu Blind">
<LI><A href="../../Campus_Life/Video_Presentation.htm">Video Presentation</A> </LI>
<LI><A href="../../Campus_Life/Campus_Tour.htm">Campus Tour</A> </LI>
<LI><A href="../../Campus_Life/Campus_Map.htm">Campus Map</A> </LI>
<LI><A href="../../Campus_Life/Housing___Dining.htm">Housing &amp; Dining</A> </LI>
<LI><A href="../../Campus_Life/Activities.htm">Activities</A> </LI>
<LI><A href="../../Campus_Life/Athletics.htm">Athletics</A> </LI>
</UL>
</LI>

</UL></DIV></DIV><!------top   end------><!------top1 start------>
<DIV id="top2" class="top-bg w100">
<DIV class="head1 w96">
<DIV class="nav"><UL class="menu">

<LI class="nav-h">
<DIV><A href="../../About/Overview.htm">About<IMG src="../../images/nav-bt.png"></A></DIV>
<UL class="submenu Blind">
<LI><A href="../../About/Overview.htm">Overview</A> </LI>
<LI><A href="../../About/Message_from_the_President.htm">Message from the President</A> </LI>
<LI><A href="../../About/Statistics___Facts.htm">Statistics &amp; Facts</A> </LI>
<LI><A href="../../About/Current_Administrators.htm">Current Administrators</A> </LI>
<LI><A href="../../About/NCUT_s_70th_Anniversary.htm">NCUT's 70th Anniversary</A> </LI>
</UL>
</LI>


<LI class="nav-h">
<DIV><A href="../../Academics1/Schools.htm">Academics<IMG src="../../images/nav-bt.png"></A></DIV>
<UL class="submenu Blind">
<LI><A href="../../Academics1/Schools.htm">Schools</A> </LI>
<LI><A href="../../Academics1/Academic_Programs.htm">Academic Programs</A> </LI>
<LI><A href="../../Academics1/Programmes_Taught_in_English.htm">Programmes Taught in English</A> </LI>
<LI><A href="../../Academics1/Research.htm">Research</A> </LI>
</UL>
</LI>


<LI class="nav-h">
<DIV><A href="../../Admissions1/Undergraduate.htm">Admissions<IMG src="../../images/nav-bt.png"></A></DIV>
<UL class="submenu Blind">
<LI><A href="../../Admissions1/Undergraduate.htm">Undergraduate</A> </LI>
<LI><A href="../../Admissions1/Graduate.htm">Graduate</A> </LI>
<LI><A href="../../Admissions1/Chinese_Language_Program.htm">Chinese Language Program</A> </LI>
<LI><A href="../../Admissions1/Tuition___Scholarship.htm">Tuition &amp; Scholarship</A> </LI>
</UL>
</LI>


<LI class="nav-h">
<DIV><A href="../../International/International_Office.htm">International<IMG src="../../images/nav-bt.png"></A></DIV>
<UL class="submenu Blind">
<LI><A href="../../International/International_Office.htm">International Office</A> </LI>
<LI><A href="../../International/International_School.htm">International School</A> </LI>
<LI><A href="../../International/Jobs.htm">Jobs</A> </LI>
</UL>
</LI>


<LI class="nav-h">
<DIV><A href="../../Campus_Life/Video_Presentation.htm">Campus Life<IMG src="../../images/nav-bt.png"></A></DIV>
<UL class="submenu Blind">
<LI><A href="../../Campus_Life/Video_Presentation.htm">Video Presentation</A> </LI>
<LI><A href="../../Campus_Life/Campus_Tour.htm">Campus Tour</A> </LI>
<LI><A href="../../Campus_Life/Campus_Map.htm">Campus Map</A> </LI>
<LI><A href="../../Campus_Life/Housing___Dining.htm">Housing &amp; Dining</A> </LI>
<LI><A href="../../Campus_Life/Activities.htm">Activities</A> </LI>
<LI><A href="../../Campus_Life/Athletics.htm">Athletics</A> </LI>
</UL>
</LI>

</UL></DIV>
<DIV class="head-r fr">
<DIV class="form"><script type="text/javascript">
    function _nl_ys_check1(){
        
        var keyword = document.getElementById('showkeycode1029611').value;
        if(keyword==null||keyword==""){
            alert("è¯·è¾å¥ä½ è¦æ£ç´¢çåå®¹ï¼");
            return false;
        }
        if(window.toFF==1)
        {
            document.getElementById("lucenenewssearchkey1029611").value = Simplized(keyword );
        }else
        {
            document.getElementById("lucenenewssearchkey1029611").value = keyword;            
        }
        var  base64 = new Base64();
        document.getElementById("lucenenewssearchkey1029611").value = base64.encode(document.getElementById("lucenenewssearchkey1029611").value);
        new VsbFormFunc().disableAutoEnable(document.getElementById("showkeycode1029611"));
        return true;
    } 
</script>
<form action="../../ssy.jsp?wbtreeid=1008" method="post" id="au5a" name="au5a" onsubmit="return _nl_ys_check1()" style="display: inline">
 <input type="hidden" id="lucenenewssearchkey1029611" name="lucenenewssearchkey" value=""><input type="hidden" id="_lucenesearchtype1029611" name="_lucenesearchtype" value="1"><input type="hidden" id="searchScope1029611" name="searchScope" value="0">
  <input name="showkeycode" id="showkeycode1029611" class="search-left fl">
         
         <input type="image" class="search-right fr" src="../../images/so-bt.png">
 
 
  
</form>
</DIV>
<DIV class="zh"><A href="http://www.ncut.edu.cn/">ä¸­æ</A>
</DIV></DIV></DIV></DIV><!------top1   end------>

<!------center start------>
<DIV class="center w96">

<script language="javascript" src="../../_dwr/interface/NewsvoteDWR.js"></script><script language="javascript" src="../../_dwr/engine.js"></script><script language="javascript" src="/system/resource/js/news/newscontent.js"></script><script language="javascript" src="/system/resource/js/ajax.js"></script><form name="_newscontent_fromname"><script language="javascript" src="/system/resource/js/jquery/jquery-latest.min.js"></script>

    <div class="con-h">Online application</div>
    <div class="con-span">
<span>


March








 16
</span>,<span>2018</span></div>
    
    
    <div class="con-tt" id="vsb_content"><div class="v_news_content">
<p>The following url is&nbsp;NCUT&nbsp;admission application&nbsp;interface of the&nbsp;Chinese language, undergraduate and graduate programs.</p>
<p><a href="https://ncut.17gz.org/member/login.do">https://ncut.17gz.org/member/login.do</a></p>
<p><span style="line-height: 0px; display: none;">â</span><br></p>
</div></div><div id="div_vote_id"></div>
        

</form>
</DIV><!------center   end------><!------part3 start------>
<DIV class="par3-bg">
<DIV class="part3 w96">
<DIV class="link-box">
<DIV class="link-h">CONTACT US</DIV>
<DIV class="icon2">     <SPAN><A href="javascript:void(0)" target="_blank">
<DIV class="icon2-con"><IMG src="../../images/code1.png"></DIV>
<DIV class="icon2-bt"><IMG src="../../images/icon1.png"></DIV>
</A></SPAN> 
 <SPAN><A href="javascript:void(0)" target="_blank">
<DIV class="icon2-con"><IMG src="../../images/code2.png"></DIV>
<DIV class="icon2-bt"><IMG src="../../images/icon2.png"></DIV>
</A></SPAN> 
 <SPAN class="s1"><A href="javascript:void(0)" target="_blank">
<IMG src="../../images/icon5.png">
</A></SPAN>
</DIV></DIV>
<DIV class="p3-box">
<DIV class="p3-ul" style="background: none transparent scroll repeat 0% 0%">
<DIV class="ul-h">About</DIV><UL>
    <LI><a href="../../About/Overview.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36837)">Overview</a></li>
    <LI><a href="../../About/Message_from_the_President.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36838)">Message from the President</a></li>
    <LI><a href="../../About/Statistics___Facts.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 38658)">Statistics &amp; Facts</a></li>
    <LI><a href="../../About/Current_Administrators.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36839)">Current Administrators</a></li>
    <LI><a href="../../About/NCUT_s_70th_Anniversary.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36840)">NCUT's 70th Anniversary</a></li>
</UL></DIV>
<DIV class="p3-ul">
<DIV class="ul-h">Academics</DIV><UL>
    <LI><a href="../../About/Overview.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36841)">Overview</a></li>
    <LI><a href="../../Academics1/Schools.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36842)">Schools &amp; Departments</a></li>
    <LI><a href="../../Academics1/Academic_Programs.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36843)">Academic Programs</a></li>
    <LI><a href="../../Academics1/Research.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36906)">Research</a></li>
    <LI><a href="http://lib.ncut.edu.cn/lib/Index.html" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36844)">Library</a></li>
</UL></DIV>
<DIV class="p3-ul">
<DIV class="ul-h">Admissions</DIV><UL>
    <LI><a href="../../Admissions1/Undergraduate.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36846)">Undergraduate</a></li>
    <LI><a href="../../Admissions1/Graduate.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36847)">Graduate</a></li>
    <LI><a href="../../Admissions1/Chinese_Language_Program.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36848)">Chinese Language Program</a></li>
    <LI><a href="../../Admissions1/Tuition___Scholarship.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36845)">Tuition &amp; Scholarship</a></li>
</UL></DIV>
<DIV class="p3-ul">
<DIV class="ul-h">International</DIV><UL>
    <LI><a href="../../International/International_Office.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36849)">International Office</a></li>
    <LI><a href="../../International/International_School.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36850)">International School</a></li>
    <LI><a href="#" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36851)">Students' life</a></li>
    <LI><a href="../../International/Jobs.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36852)">Jobs</a></li>
</UL></DIV>
<DIV class="p3-ul">
<DIV class="ul-h">Campus Life</DIV><UL>
    <LI><a href="../../Campus_Life/Video_Presentation.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36853)">Video Presentation</a></li>
    <LI><a href="../../Campus_Life/Campus_Tour.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36854)">Campus Tour</a></li>
    <LI><a href="../../Campus_Life/Campus_Map.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36855)">Campus Map</a></li>
    <LI><a href="../../Campus_Life/Housing___Dining.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36856)">Housing &amp; Dining</a></li>
    <LI><a href="../../Campus_Life/Activities.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36908)">Activities</a></li>
    <LI><a href="../../Campus_Life/Athletics.htm" title="" onclick="_addDynClicks(&#34;wburl&#34;, 1399944793, 36907)">Athletics</a></li>
</UL></DIV></DIV></DIV></DIV><!------part3   end------><!------foot start------>
<DIV class="foot-bg w100">
<DIV class="foot w96"><!-- çæåå®¹è¯·å¨æ¬ç»ä»¶"åå®¹éç½®-çæ"å¤å¡«å -->
<p style="text-align: center"><em>No. 5 Jinyuanzhuang Road, Shijingshan District Beijing, P.R. China 100144</em>|<em>86-10-88802114</em>|<em>Â© 2017 NCUT All Rights Reserved</em></p></DIV></DIV><!------foot   end------>

</BODY></HTML>

"""

ioc_find_regex = re.compile(r'('
                            r'http[s]?://[\w\-.:]+\w+[\w./?&=+#%-]+|'
                            r'(?:[\w\-]+\.){1,16}\w+(?::\d+)?[/?][\w./?&=+#%-]+|'
                            r'\b(?<![@/])(?:[\w-]+\.)+[0-9a-zA-Z]+'      # 忽略邮箱和url： test@126.com, ../1235/7214.htm
                            r')')

print(ioc_find_regex.findall(s))
