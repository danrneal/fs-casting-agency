/* globals Handlebars */

import { addPagination, auth, flashMessage } from './utils.js';

/**
 * @description Class representing a movie.
 * @class
 */
class Movie {
  /**
   * @callback movieCallback
   * @param {number} page - number of page to retrieve data for
   */

  /**
   * @description Create a Movie object
   * @param {Object} movie - object containing data for the movie to create
   * @param {movieCallback} callback - callback function to be called after a db change
   */
  constructor(movie, callback) {
    this.id = movie.id;
    this.title = movie.title;
    this.releaseDate = movie.release_date;
    this.actors = movie.actors;
    this.poster = movie.poster;
    this.callback = callback;
  }

  /**
   * @description Create a new movie in the db
   * @param {Object} form - form containing data for the movie to create
   */
  create(form) {
    const actors = form.actors.value
      .split(/[\n,]+/)
      .map((actor) => actor.trim())
      .filter((actor) => actor !== '');
    fetch('/api/movies', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${auth.token}`,
      },
      body: JSON.stringify({
        title: form.title.value || null,
        release_date: form.releaseDate.value || null,
        actors,
        poster: form.poster.value || null,
      }),
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) throw new Error();
        $('#modal').modal('hide');

        const activePage = document.querySelector('.page-item.active');
        const { page } = activePage.dataset;
        this.callback(page);
        flashMessage(
          'success',
          '&#10004; SUCCESS',
          'Movie successfully created!'
        );
      })
      .catch(() => {
        form.actors.setCustomValidity('invalid');
      });
  }

  /**
   * @description Update the movie in the db
   * @param {Object} form - form containing data to update the movie with
   */
  update(form) {
    const actors = form.actors.value
      .split(/[\n,]+/)
      .map((actor) => actor.trim())
      .filter((actor) => actor !== '');
    fetch(`/api/movies/${this.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${auth.token}`,
      },
      body: JSON.stringify({
        title: form.title.value || null,
        release_date: form.releaseDate.value || null,
        actors,
        poster: form.poster.value || null,
      }),
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) throw new Error();
        $('#modal').modal('hide');

        const activePage = document.querySelector('.page-item.active');
        const { page } = activePage.dataset;
        this.callback(page);
        flashMessage(
          'success',
          '&#10004; SUCCESS',
          'Movie successfully updated!'
        );
      })
      .catch(() => {
        form.actors.setCustomValidity('invalid');
      });
  }

  /**
   * @description Delete the movie from the db
   */
  delete() {
    $('#modal').modal('hide');
    fetch(`/api/movies/${this.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${auth.token}` },
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data.success) throw new Error();

        const activePage = document.querySelector('.page-item.active');
        const { page } = activePage.dataset;
        this.callback(page);
        flashMessage(
          'success',
          '&#10004; SUCCESS',
          'Movie successfully deleted!'
        );
      })
      .catch(() => {
        flashMessage('danger', '&#10008; ERROR', 'An unknown error occurred!');
      });
  }

  /**
   * @description Create a form to create a new movie
   * @return {Object} html object containing the created form
   */
  creationForm() {
    const formTemplate = Handlebars.compile(
      document.querySelector('#movie-form').innerHTML
    );
    const header = 'Create New Movie';
    let creationForm = formTemplate({ header });

    const div = document.createElement('div');
    div.innerHTML = creationForm;
    creationForm = div;

    creationForm.onsubmit = (event) => {
      event.preventDefault();
      const form = creationForm.lastElementChild;
      form.actors.setCustomValidity('');
      if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
      } else {
        this.create(form);
      }
      form.classList.add('was-validated');
    };

    return creationForm;
  }

  /**
   * @description Create a form to edit the movie
   * @return {Object} html object containing the created form
   */
  updateForm() {
    const formTemplate = Handlebars.compile(
      document.querySelector('#movie-form').innerHTML
    );
    const header = `Editing: ${this.title}`;
    const actors = this.actors.map((actor) => actor.name).join(',\n');
    let updateForm = formTemplate({
      header,
      title: this.title,
      releaseDate: this.releaseDate,
      actors,
      poster: this.poster,
    });

    const div = document.createElement('div');
    div.innerHTML = updateForm;
    updateForm = div;

    updateForm.onsubmit = (event) => {
      event.preventDefault();
      const form = updateForm.lastElementChild;
      form.actors.setCustomValidity('');
      if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
      } else {
        this.update(form);
      }
      form.classList.add('was-validated');
    };

    return updateForm;
  }

  /**
   * @description Create a modal to view the movie
   * @return {Object} html object containing the created modal
   */
  modal() {
    const modalTemplate = Handlebars.compile(
      document.querySelector('#movie-modal').innerHTML
    );
    let modal = modalTemplate({
      title: this.title,
      releaseDate: this.releaseDate,
      poster: this.poster,
      actors: this.actors,
    });

    const div = document.createElement('div');
    div.innerHTML = modal;
    modal = div;

    if (auth.perms.includes('update:movies')) {
      const editBtn = modal.querySelector('#edit-btn');
      editBtn.classList.remove('hidden');
      editBtn.onclick = () => {
        const movieForm = this.updateForm();
        const modalContent = document.querySelector('.modal-content');
        modalContent.innerHTML = '';
        modalContent.appendChild(movieForm);
      };
    }

    if (auth.perms.includes('delete:movies')) {
      const deleteBtn = modal.querySelector('#delete-btn');
      deleteBtn.classList.remove('hidden');
      deleteBtn.onclick = () => {
        this.delete();
      };
    }

    return modal;
  }

  /**
   * @description Create a card to view the movie
   * @return {Object} html object containing the created card
   */
  card() {
    const cardTemplate = Handlebars.compile(
      document.querySelector('#movie-card').innerHTML
    );
    let year;
    if (this.releaseDate) [year] = this.releaseDate.split('-');
    let card = cardTemplate({
      title: this.title,
      year,
      poster: this.poster,
    });

    const div = document.createElement('div');
    div.innerHTML = card;
    card = div.firstElementChild;

    card.onclick = () => {
      const movieModal = this.modal();
      const modalContent = document.querySelector('.modal-content');
      modalContent.innerHTML = '';
      modalContent.appendChild(movieModal);
      $('#modal').modal('show');
    };

    return card;
  }
}

/**
 * @description Fetch movies and add them to the page
 * @param {number} page - page number to retrieve movies for
 */
export default function showMovies(page) {
  const navMovies = document.querySelector('#nav-movies');
  const navActors = document.querySelector('#nav-actors');
  const modal = document.querySelector('#modal');
  const createBtn = document.querySelector('#create-btn');
  navMovies.classList.add('active');
  navActors.classList.remove('active');
  modal.classList.remove('actor-modal');
  modal.classList.add('movie-modal');

  if (auth.perms.includes('create:movies')) {
    createBtn.innerHTML = '&#10010; CREATE NEW MOVIE';
    createBtn.parentElement.classList.remove('hidden');
    createBtn.onclick = () => {
      const newMovie = new Movie({}, showMovies);
      const newMovieForm = newMovie.creationForm();
      const modalContent = document.querySelector('.modal-content');
      modalContent.innerHTML = '';
      modalContent.appendChild(newMovieForm);
      $('#modal').modal('show');
    };
  } else {
    createBtn.parentElement.classList.add('hidden');
  }

  fetch(`/api/movies?page=${page}`, {
    method: 'GET',
    headers: { Authorization: `Bearer ${auth.token}` },
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      if (!data.success) throw new Error();

      const content = document.querySelector('#content');
      content.innerHTML = '';
      data.movies.forEach((movie) => {
        const newMovie = new Movie(movie, showMovies);
        const movieCard = newMovie.card();
        content.appendChild(movieCard);
      });

      const totalPages = Math.ceil(data.total_movies / 25);
      addPagination(totalPages, page, '/movies', showMovies);
    })
    .catch(() => {
      flashMessage('danger', '&#10008; ERROR', 'An unknown error occurred!');
    });

  window.scrollTo(0, 0);
}
