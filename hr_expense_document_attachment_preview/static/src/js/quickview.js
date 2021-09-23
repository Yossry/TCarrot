//-*- coding: utf-8 -*-
odoo.define('hr_expense_document_attachment_preview.quickview', function(require) {
    'use strict';

    var ajax = require('web.ajax');
    var BasicRenderer = require('web.BasicRenderer');
    var config = require('web.config');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var dom = require('web.dom');
    var field_utils = require('web.field_utils');
    var Pager = require('web.Pager');
    var utils = require('web.utils');
    var ListRenderer = require('web.ListRenderer');
    var BasicView = require('web.BasicView');
    var core = require('web.core');
    var ListController = require('web.ListController');

    var qweb = core.qweb;
    var _t = core._t;

    var internal = {
        extract_all_pdf_img: true
    };

    internal.pdfConverter = function(pdf_file, callback_page, callback) {
        PDFJS.workerSrc = '/hr_expense_document_attachment_preview/static/vendor/pdfjs/pdf.worker.js';

        var loading_task = PDFJS.getDocument(pdf_file);
        loading_task.promise.then(
            function(pdf) {
                var page_number = 1;
                var max_pages;
                if (internal.extract_all_pdf_img === true) {
                    max_pages = pdf.pdfInfo.numPages;
                } else {
                    max_pages = 1;
                }

                var promises_page = [];
                for (; page_number <= max_pages; page_number++) {
                    promises_page[page_number - 1] = new Promise((resolve, reject) => {
                        pdf.getPage(page_number).then(function(page) {
                            var scale = 1.5;
                            var viewport = page.getViewport(scale);

                            // Prepare canvas using PDF page dimensions
                            var canvas = document.createElement('canvas');
                            var context = canvas.getContext('2d');
                            canvas.height = viewport.height;
                            canvas.width = viewport.width;

                            // Render PDF page into canvas context
                            var renderContext = {
                                canvasContext: context,
                                viewport: viewport
                            };

                            var renderTask = page.render(renderContext);
                            renderTask.then(function() {
                                callback_page(canvas.toDataURL());
                                resolve();
                            });
                        });
                    });
                }

                Promise.all(promises_page).then((values) => {
                    callback();
                });
            },
            function(reason) {
                console.error('Fail to read PDF : ' + reason);
            }
        );
    };

    ListRenderer.include({
        custom_events: _.extend({}, ListRenderer.prototype.custom_events, {
            button_clicked: '_onBtnClick',
        }),
        _onBtnClick: function (event) {
            var sel_line_id = event.data.record.res_id; //$(this).closest('tr')[0].baseURI.split('#')[1].split('&')[0].split('=')[1];
            if (sel_line_id && event.data.attrs['id'] == "expense") {
                ajax.jsonRpc("/preview", 'call', {'line_id': sel_line_id}).then(function(res) {
                    var image_regex = new RegExp('\\.(jpe?g|png|gif)$', 'i');
                    var doc_regex = new RegExp('\\.do(c|t)x?$', 'i');
                    var xls_regex = new RegExp('\\.xlsx?$', 'i');
                    var pdf_regex = new RegExp('\\.pdf$', 'i');
                    var ppt_regex = new RegExp('\\.pptx?$', 'i');
                    var main_div_id = 'attachment_quickview';
                    var main_div = '<div id="' + main_div_id + '" style="display:none;" class="oe_form_sheet o_form_sheet">' +
                        '<div class="oe_horizontal_separator o_horizontal_separator oe_clear">' + '</div>' +
                        '<div class="container-quickview"></div>' +
                        '</div>';
                    var a_preview_tpl = '<a id="pre_link" href="%download%">' +
                        '<img src="%img%" %img-box% />' +
                        '<div>%name%</div>' +
                        '</a>';
                    var div_preview_tpl = '<div class="attachment-quickview-item" id="attachment-quickview-item-%id%">' +
                        a_preview_tpl +
                        '</div>';

                    var $main_div = $('#' + main_div_id);

                    if (res.length === 0) {
                        $main_div.remove();
                    }

                    if ($main_div.length === 0) {
                        if ($('#attachment_preview').length > 0) {
                            $('#attachment_preview').before(main_div);
                        } else {
                            $('.oe_form_sheetbg, .o_form_sheet_bg').append(main_div);
                        }
                        $main_div = $('#' + main_div_id);
                    }

                    var $preview_container = $main_div.find('.container-quickview');
                    $preview_container.html('');
                    var pdf = false;
                    res.forEach(function(attachment) {
                        var img = '/hr_expense_document_attachment_preview/static/img/raw.svg';
                        var img_box = '';

                        if (image_regex.test(attachment.name) === true) {
                            img = '/web/content/' + attachment.id + '?download=false';
                            img_box = 'data-touchtouch="' + img + '"';
                        } else if (doc_regex.test(attachment.name) === true) {
                            img = '/hr_expense_document_attachment_preview/static/img/doc.svg';
                        } else if (xls_regex.test(attachment.name) === true) {
                            img = '/hr_expense_document_attachment_preview/static/img/xls.svg';
                        } else if (pdf_regex.test(attachment.name) === true) {
                            img = '/hr_expense_document_attachment_preview/static/img/pdf.svg';
                            pdf = true;
                        } else if (ppt_regex.test(attachment.name) === true) {
                            img = '/hr_expense_document_attachment_preview/static/img/ppt.svg';
                        }

                        var div_preview = div_preview_tpl
                            .replace('%id%', attachment.id)
                            .replace('%download%', attachment.url)
                            .replace('%img%', img)
                            .replace('%name%', attachment.name)
                            .replace('%img-box%', img_box);
                        $preview_container.append(div_preview);


                        if (pdf_regex.test(attachment.name) === true) {
                            internal.pdfConverter('/web/content/' + attachment.id + '?download=false', function(data_url) {
                                var a_preview = a_preview_tpl
                                    .replace('%download%', attachment.url)
                                    .replace('%img%', data_url)
                                    .replace('%name%', attachment.name)
                                    .replace('%img-box%', 'data-touchtouch="' + data_url + '"');
                                $preview_container.find('#attachment-quickview-item-' + attachment.id).append(a_preview);
                            }, function() {
                                $preview_container.find('#attachment-quickview-item-' + attachment.id).find('a').eq(0).remove();
                                $preview_container.find('[data-touchtouch]').touchTouch();
                                $preview_container.find('[data-touchtouch]')[0].click();
                            });
                        }
                    });
                    $('#galleryOverlay').remove();
                    $preview_container.find('[data-touchtouch]').touchTouch();
                    $('.container-preview').find('[data-touchtouch]').touchTouch();
                    if (!pdf && $preview_container.find('[data-touchtouch]').length > 0) {
                        $preview_container.find('[data-touchtouch]')[0].click();
                    }

                });
            }
        },
        _renderRow: function (record, index) {
            var self = this;
            var $cells = this.columns.map(function (node, index) {
                return self._renderBodyCell(record, node, index, { mode: 'readonly' });
            });

            var $tr = $('<tr/>', {class: 'o_data_row'})
                .attr('data-id', record.id)
                .append($cells);
            if (this.hasSelectors) {
                $tr.prepend(this._renderSelector('td', !record.res_id));
            }
            if (this.addTrashIcon) {
                var $icon = this.isMany2Many ?
                    $('<button>', {class: 'fa fa-times', 'name': 'unlink', 'aria-label': _t('Unlink row ') + (index + 1)}) :
                    $('<button>', {class: 'fa fa-trash-o', 'name': 'delete', 'aria-label': _t('Delete row ') + (index + 1)});
                var $td = $('<td>', {class: 'o_list_record_remove'}).append($icon);
                $tr.append($td);
            }
            this._setDecorationClasses($tr, this.rowDecorations, record);
            return $tr;
        },

    });
});
