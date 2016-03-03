#!c:/Python27/python -u


print "<!DOCTYPE html> +\
<html lang='en'>        +\
<head>                  +\
	<meta charset='utf-8'> +\
	<meta content='General' name='rating'/> +\
	<link type='text/plain' rel='author' href='http://news.ncsu.edu/humans.txt' /> +\
	<title>  STR Database</title>                                                  +\
	<script>                                                                       +\
	// Picture element HTML5 shiv                                                  +\
	document.createElement( 'picture' );                                           +\
	</script>                                                                      +\
	<script src='https://news.ncsu.edu/wp-content/themes/ncstate-news/js/picturefill.js' async></script> +\
	<!-- Styles -->                                                                +\
	<link href='https://cdn.ncsu.edu/brand-assets/bootstrap/css/bootstrap.css' rel='stylesheet' media='screen' type='text/css' />  +\
	<link href='https://cdn.ncsu.edu/brand-assets/fonts/print-only.css' rel='stylesheet' type='text/css' />                        +\
	<link href='https://news.ncsu.edu/wp-content/themes/ncstate-news/style.css?1449694735' rel='stylesheet' media='screen' type='text/css' />  +\
	<link href='https://news.ncsu.edu/wp-content/themes/ncstate-news/print.css' rel='stylesheet' media='print' type='text/css'/>   +\
	<link rel='stylesheet' href='https://news.ncsu.edu/wp-content/themes/ncstate-news/css/fancybox/jquery.fancybox.css?v=2.0.6' type='text/css' media='screen' />  +\
	<link rel='stylesheet' href='https://news.ncsu.edu/wp-content/themes/ncstate-news/css/fancybox/jquery.fancybox-buttons.css?v=1.0.2' type='text/css' media='screen' />  +\
	<meta name='viewport' content='width=device-width, user-scalable=no, initial-scale=1, maximum-scale=1' />  +\
    <script src='https://cdn.ncsu.edu/brand-assets/utility-bar/ub-ga.php'></script> +\
	<!--[if lt IE 9]>                                                              +\
	    <script src='http://html5shim.googlecode.com/svn/trunk/html5.js'></script> +\
	<![endif]-->                                                                   +\
	<link rel='alternate' type='application/rss+xml' title='NC State News &raquo; CSI: NC State Comments Feed' href='https://news.ncsu.edu/2012/01/csi-nc-state/feed/' /> +\
    <link rel='stylesheet' id='events_map_style-css'  href='https://news.ncsu.edu/wp-content/plugins/ncstate-events/css/style.css?ver=4.3.1' type='text/css' media='all' /> +\
    <script type='text/javascript' src='https://maps.googleapis.com/maps/api/js?v=3&#038;ver=4.3.1'></script>   +\
    <meta name='generator' content='WordPress 4.3.1' />                     +\
    <link rel='canonical' href='https://news.ncsu.edu/2012/01/csi-nc-state/' /> +\
    <link rel='shortlink' href='https://news.ncsu.edu/?p=6607' />           +\
    <link rel='https://github.com/WP-API/WP-API' href='https://news.ncsu.edu/wp-json' />    +\
</head> +\
<body>  +\
<div id='ncstate-utility-bar'></div> +\
<div class='primary-nav'>   +\
	<div class='container'>   +\
	<h2 class='blog-menu-heading-text'><a href='/'>NC State News</a></h2>    +\
	<ul id='menu-primary-nav' class='blog-menu list-unstyled' aria-label='Main Menu'>    +\
	   <li id='menu-item-142034' class='menu-item menu-item-type-taxonomy menu-item-object-category current-post-ancestor current-menu-parent current-post-parent menu-item-has-children menu-item-142034'><a href='https://news.ncsu.edu/category/research-and-innovation/'>Research and Innovation</a>    +\
       <ul class='sub-menu list-unstyled'>    +\
	       <li id='menu-item-142036' class='menu-item menu-item-type-taxonomy menu-item-object-category menu-item-142036'><a href='https://news.ncsu.edu/category/research-and-innovation/the-abstract/'>The Abstract</a></li>    +\
	       <li id='menu-item-142035' class='menu-item menu-item-type-taxonomy menu-item-object-category current-post-ancestor current-menu-parent current-post-parent menu-item-142035'><a href='https://news.ncsu.edu/category/research-and-innovation/partners/'>Partners</a></li>    +\
        </ul>    +\
        </li>      +\
        <li id='menu-item-142024' class='menu-item menu-item-type-taxonomy menu-item-object-category current-post-ancestor current-menu-parent current-post-parent menu-item-has-children menu-item-142024'><a href='https://news.ncsu.edu/category/campus-life/'>Campus Life</a>    +\
        <ul class='sub-menu list-unstyled'>    +\
	       <li id='menu-item-142025' class='menu-item menu-item-type-taxonomy menu-item-object-category current-post-ancestor current-menu-parent current-post-parent menu-item-142025'><a href='https://news.ncsu.edu/category/campus-life/academics/'>Academics</a></li>    +\
	       <li id='menu-item-142027' class='menu-item menu-item-type-taxonomy menu-item-object-category menu-item-142027'><a href='https://news.ncsu.edu/category/campus-life/athletics/'>Athletics</a></li>    +\
	       <li id='menu-item-142028' class='menu-item menu-item-type-taxonomy menu-item-object-category menu-item-142028'><a href='https://news.ncsu.edu/category/campus-life/events/'>Events</a></li>          +\
           <li id='menu-item-142029' class='menu-item menu-item-type-taxonomy menu-item-object-category menu-item-142029'><a href='https://news.ncsu.edu/category/campus-life/students/'>Students</a></li>      +\
        </ul>          +\
        </li>          +\
        <li id='menu-item-142030' class='menu-item menu-item-type-taxonomy menu-item-object-category current-post-ancestor current-menu-parent current-post-parent menu-item-has-children menu-item-142030'><a href='https://news.ncsu.edu/category/faculty-and-staff/'>Faculty and Staff</a>    +\
        <ul class='sub-menu list-unstyled'>    +\
	       <li id='menu-item-142033' class='menu-item menu-item-type-taxonomy menu-item-object-category menu-item-142033'><a href='https://news.ncsu.edu/category/faculty-and-staff/hr-finance/'>HR and Finance</a></li>           +\
	       <li id='menu-item-142031' class='menu-item menu-item-type-taxonomy menu-item-object-category menu-item-142031'><a href='https://news.ncsu.edu/category/faculty-and-staff/awards-honors/'>Awards and Honors</a></li>     +\
	       <li id='menu-item-142032' class='menu-item menu-item-type-taxonomy menu-item-object-category menu-item-142032'><a href='https://news.ncsu.edu/category/faculty-and-staff/faculty-focus/'>Faculty Focus</a></li>         +\
        </ul>    +\
        </li>    +\
        <li id='menu-item-142037' class='menu-item menu-item-type-taxonomy menu-item-object-category menu-item-has-children menu-item-142037'><a href='https://news.ncsu.edu/category/service-and-community/'>Service and Community</a>    +\
        <ul class='sub-menu list-unstyled'>    +\
	       <li id='menu-item-142026' class='menu-item menu-item-type-taxonomy menu-item-object-category menu-item-142026'><a href='https://news.ncsu.edu/category/service-and-community/alumni/'>Alumni</a></li>    +\
        </ul>    +\
        </li>    +\
        <li id='menu-item-142701' class='menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children menu-item-142701'><a href='https://news.ncsu.edu/for-media/'>For Media</a>    +\
        <ul class='sub-menu list-unstyled'>    +\
	       <li id='menu-item-143351' class='menu-item menu-item-type-custom menu-item-object-custom menu-item-143351'><a href='/news-releases'>News Releases</a></li>                                  +\
	       <li id='menu-item-145351' class='menu-item menu-item-type-custom menu-item-object-custom menu-item-145351'><a href='/in-the-news/'>In the News</a></li>                                     +\
	       <li id='menu-item-142751' class='menu-item menu-item-type-custom menu-item-object-custom menu-item-142751'><a href='http://www.ncsu.edu/experts/'>Experts</a></li>                          +\
	       <li id='menu-item-221601' class='menu-item menu-item-type-post_type menu-item-object-page menu-item-221601'><a href='https://news.ncsu.edu/for-media/tv-studio/'>TV Studio</a></li>         +\
        </ul>    +\
        </li>    +\
        <li id='menu-item-142721' class='menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children menu-item-142721'><a href='https://news.ncsu.edu/about/'>About NC State News</a>      +\
        <ul class='sub-menu list-unstyled'>    +\
	       <li id='menu-item-142731' class='menu-item menu-item-type-post_type menu-item-object-page menu-item-142731'><a href='https://news.ncsu.edu/about/contact/'>Contact</a></li>                 +\
	       <li id='menu-item-142741' class='menu-item menu-item-type-post_type menu-item-object-page menu-item-142741'><a href='https://news.ncsu.edu/about/send-a-tip/'>Send a Tip</a></li>           +\
        </ul>    +\
        </li>    +\
        <li class='menu-item search-item'>    +\
		<div class='glyphicon glyphicon-search search-icon'></div>    +\
		<div class='masthead-search'>    +\
		</div>    +\
        </li>    +\
	</ul>    +\
	</div>    +\
</div>    +\
<div id='main-content' >     +\
    <div class='container'>    +\
        <header style='width:100%;'>   +\
            <h1 class='post-title' itemprop='name'>Forensic Databases</h1>   +\
        </header>   +\
    </div>          +\
    <div class='container'>  "

"""
            <div class='section-article'>   +\
                <div class='article-content col-md-9 col-sm-12'>   +\
                    <section class='entry-content'>   +\
                    </section>   +\
                </div>     +\
            </div> "
"""
