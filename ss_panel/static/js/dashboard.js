$(function () {
	//Clipboard
	var clipboard = new Clipboard('.input-copy .btn');

	clipboard.on('success', function(e) {
	    $('.input-copy .btn span').addClass('not-visible');
	    $('.input-copy .check-animate').removeClass('hidden');
	    $('.copy-message').removeClass('hidden');
	
	    e.clearSelection();
	});
	
	//iCheck
    $('.page-content').find('input').iCheck({
        inheritID: true,
        checkboxClass: 'checkbox-styled',
        radioClass: 'radio-styled',
        increaseArea: '20%'
    });
    
	// BootStrap Modal
	$('body').append($('#modalAjax'));
	
	//Select2
	$('select').select2({
		minimumResultsForSearch: Infinity
	});
	
	//owlCarousel
	$('.owl-carousel').owlCarousel({
	    animateOut: 'fadeOut',
		items:1,
		margin:10,
		autoHeight:true,
	    loop: true,
	    autoplay:true,
	    mouseDrag:false,
	    autoplayTimeout: 8000,
	    autoplayHoverPause:true
	});
	
	//lazyload
	$("img.coverimage").lazyload({
	    threshold : 100,
	    effect : "fadeIn"
    });
    
    $('.cards-carousel').each(function () {
        var
            $this = $(this)
            , $cards = $this.find('.cards');
        var slider = $cards.lightSlider({
            item: 1
            , loop: false
            , slideMove: 1
            , slideMargin: 0
            , easing: 'cubic-bezier(0.25, 0, 0.25, 1)'
            , speed: 600
            , onBeforeSlide: function (el) {
                var
                    current = (el.getCurrentSlideCount() + slider.find('.clone').length / 2)
                    , pageCurrent = (current - 1) * 4 + $cards.find('> li:nth-child(' + current + ') > a').length;
                $this.find('.number-current').html(pageCurrent);
            }
        });
        $this.find('.card-prev').click(function () {
            slider.goToPrevSlide();
        });
        $this.find('.card-next').click(function () {
            slider.goToNextSlide();
        });
    });
});