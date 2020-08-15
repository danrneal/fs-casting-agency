/* globals Handlebars */

export const auth = {
  token: null,
  perms: [],
};

/**
 * @description Flash a message in the form of a toast
 * @param {string} category - category of Bootstrap alert to flash
 * @param {string} header - header of the toast
 * @param {string} message - body of the toast
 */
export function flashMessage(category, header, message) {
  const toast = document.querySelector('.toast');
  const toastHeader = document.querySelector('.toast-header');
  const toastBody = document.querySelector('.toast-body');
  toast.classList.add(`border-${category}`);
  toastHeader.firstElementChild.innerHTML = header;
  toastBody.innerHTML = message;
  $('.toast').on('hidden.bs.toast', () => {
    toast.classList.remove(`border-${category}`);
    toastHeader.firstElementChild.innerHTML = '';
    toastBody.innerHTML = '';
  });
  $('.toast').toast('show');
}

/**
 * @callback pageCallback
 * @param {number} page - number of page to retrieve data for
 */

/**
 * @description Add pagination element to page
 * @param {number} totalPages - total number of pages returned from the api
 * @param {number} page - number of the current page
 * @param {string} route - route of the current url
 * @param {pageCallback} callback - callback function to be called on a click event
 */
export function addPagination(totalPages, page, route, callback) {
  const pages = [...Array(totalPages + 1).keys()];
  pages.shift();

  const paginationTemplate = Handlebars.compile(
    document.querySelector('#pagination').innerHTML
  );

  const pagination = paginationTemplate({
    pages,
    firstPage: parseInt(page, 10) === 1,
    lastPage: parseInt(page, 10) === totalPages,
  });
  const paginators = document.querySelectorAll('.pagination');
  paginators.forEach((paginator) => {
    const p = paginator;
    p.innerHTML = pagination;
  });

  const currentPages = document.querySelectorAll(`[data-page="${page}"]`);
  currentPages.forEach((pageItem) => {
    pageItem.classList.add('active');
  });

  const pageItems = document.querySelectorAll('.page-item');
  pageItems.forEach((pageItem) => {
    if (!pageItem.classList.contains('disabled')) {
      const item = pageItem;
      item.onclick = (event) => {
        event.preventDefault();
        if (!pageItem.classList.contains('active')) {
          let pageNum = event.target.parentElement.dataset.page;
          if (pageNum === 'prev') {
            pageNum = parseInt(page, 10) - 1;
          } else if (pageNum === 'next') {
            pageNum = parseInt(page, 10) + 1;
          }
          window.history.pushState(
            { route, page: pageNum },
            document.title,
            `${route}/${pageNum}`
          );
          callback(pageNum);
        }
      };
    }
  });
}
