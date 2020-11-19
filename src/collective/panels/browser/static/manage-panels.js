define("pat-manage-panels", [
  'jquery',
  'pat-base',
  'mockup-utils',
  'mockup-patterns-modal',
  'translate',
  'pat-logger'
], function ($, Base, utils, Modal, _t, logger) {
  'use strict';

  var log = logger.getLogger('pat-manage-panels');

  var ManagePanels = Base.extend({
    name: 'collective-panels',
    trigger: '.pat-manage-panels',
    parser: 'mockup',
    messageTimeout: 0,
    submitTimeout: 0,
    switchTimeout: 0,
    isModal: false,
    dirty: false,
    init: function(){
      var that = this;
      var $modal = that.$el.parents('.plone-modal');
      if($modal.size() === 1){
        this.isModal = true;
        /* want to do something on exit from modal now */
        var modal = $modal.data('pattern-plone-modal');
        modal.on('hide', function(){
          if(that.dirty){
            window.location.reload();
          }
        });
        that.loading = modal.loading;
      }else{
        that.loading = utils.loading;
      }
      that.bind();
    },
    bind: function(){
      var that = this;
//      that.setupAddDropdown();
      that.setupSwitchPanelManager();
//      that.setupSavePortletsSettings();
//      that.setupPortletEdit();
      if(that.isModal){
        /* if we're in a modal, it's possible we have a link to
           parent case, bind the link so we can reload modal */
        $('.panels-link-to-parent').off('click').click(function(e){
          that.loading.show();
          var $el = $(this);
          e.preventDefault();
          $.ajax({
            url: $el.attr('href'),
            data: {
              ajax_load: 1
            }
          }).done(function(html){
            var $body = $(utils.parseBodyTag(html));
            var $modal = $el.parents('.plone-modal-body');
            $modal.empty();
            var $content = $('#content', $body);
            var $h1 = $('h1', $content);
            $('.plone-modal-header', $modal.parent()).find('h2').html($h1.html());
            $h1.remove();
            $modal.append($content);
            that.rebind($('.pat-manage-panels', $content), true);
            that.loading.hide();
          });
        });
      }
    },
    rebind: function($el, suppress){
      log.info('rebind');
      if ($.contains(document, this.$el[0])) {
        // $el is not detached, replace it
        this.$el.replaceWith($el);
      }
      this.$el = $el;
      this.bind();
      if(!suppress){
        this.statusMessage();
      }
      this.dirty = true;
    },
    statusMessage: function(msg){
      if(msg === undefined){
        msg = _t("Panel changes saved");
      }
      var that = this;

      var $message = $('#panel-message');
      if($message.size() === 0){
        $message = $('<div class="portalMessage info" id="panel-message" style="opacity: 0"></div>');
        if(that.isModal){
          $('.plone-modal-body:visible').prepend($message);
        }else{
          $('#content-core').prepend($message);
        }
      }
      $message.html('<strong>' + _t("Info") + '</strong>' + msg);
      clearTimeout(that.messageTimeout);
      $message.fadeTo(500, 1);
      that.messageTimeout = window.setTimeout(function(){
        $message.fadeTo(500, 0.6);
      }, 3000);
    },
    setupAddDropdown: function(){
      var that = this;
      $('.add-panel', that.$el).change(function(e){
        e.preventDefault();
        var $select = $(this);
        var $form = $select.parents('form');
        var contextUrl = $select.attr('data-context-url');
        var url = contextUrl + $select.val() +
          '?_authenticator=' + $('[name="_authenticator"]').val() +
          '&referer=' + $('[name="referer"]', $form).val();
        that.showEditPortlet(url);
      });
    },
    setupSwitchPanelManager: function(){
      var that = this;
      $('#main-container').on('change', '.switch-panel-manager', function(e){
        e.stopImmediatePropagation();
        log.info('switch panel manager');
        console.log('switch')
        var url_ = $(this).val();
        clearTimeout(that.switchTimeout);
        that.switchTimeout = window.setTimeout(function() {
          that._reloadPanelManager(url_);
        }, 100);
      });
      // Handle back/forward browser buttons
      $(window).on('popstate', function(e) {
        e.stopImmediatePropagation();
        if (e && e.state === undefined) {
          var url_ = window.location.href;
          log.info("redirecting to: " + url_);
          that._reloadPanelManager(url_, true);
        }
      });
    },
    _reloadPanelManager: function(url_, is_popstate){
      var that = this;
      that.loading.show();
      $.get(url_, {ajax_load: 1}).done(function(html) {
        var $html = $(utils.parseBodyTag(html));
        var $content = ('#content', $html);
        $('#content').html($content);
        that.rebind($('.pat-manage-panels', $content), true);
        if (!is_popstate) {
          window.history.pushState(null, null, url_);
        } else {
          window.history.replaceState(null, null, url_);
        }
        that.loading.hide();
      });
    }
  });

  return ManagePanels;
});
