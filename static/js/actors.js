/* globals Handlebars */

import { addPagination, auth, flashMessage } from './utils.js';

/**
 * @description Class representing an actor.
 * @class
 */
class Actor {
  /**
   * @callback actorCallback
   * @param {number} page - number of page to retrieve data for
   */

  /**
   * @description Create an Actor object
   * @param {Object} actor - object containing data of the actor to create
   * @param {actorCallback} callback - callback function to be called after a db change
   */
  constructor(actor, callback) {
    this.id = actor.id;
    this.name = actor.name;
    this.birthdate = actor.birthdate;
    this.gender = actor.gender;
    this.movies = actor.movies;
    this.image = actor.image;
    this.callback = callback;
  }

  /**
   * @description Create a new actor in the db
   * @param {Object} form - form containing data for the actor to create
   */
  create(form) {
    const movies = form.movies.value
      .split(/[\n,]+/)
      .map((movie) => movie.trim())
      .filter((movie) => movie !== '');
    fetch('/api/actors', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${auth.token}`,
      },
      body: JSON.stringify({
        name: form.name.value || null,
        birthdate: form.birthdate.value || null,
        gender: form.gender.value || null,
        movies,
        image: form.image.value || null,
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
          'Actor successfully created!'
        );
      })
      .catch(() => {
        form.movies.setCustomValidity('invalid');
      });
  }

  /**
   * @description Update the actor in the db
   * @param {Object} form - form containing data for actor to update
   */
  update(form) {
    const movies = form.movies.value
      .split(/[\n,]+/)
      .map((movie) => movie.trim())
      .filter((movie) => movie !== '');
    fetch(`/api/actors/${this.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${auth.token}`,
      },
      body: JSON.stringify({
        name: form.name.value || null,
        birthdate: form.birthdate.value || null,
        gender: form.gender.value || null,
        movies,
        image: form.image.value || null,
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
          'Actor successfully updated!'
        );
      })
      .catch(() => {
        form.movies.setCustomValidity('invalid');
      });
  }

  /**
   * @description Delete the actor from the db
   */
  delete() {
    $('#modal').modal('hide');
    fetch(`/api/actors/${this.id}`, {
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
          'Actor successfully deleted!'
        );
      })
      .catch(() => {
        flashMessage('danger', '&#10008; ERROR', 'An unknown error occurred!');
      });
  }

  /**
   * @description Create a form to create a new actor
   * @return {Object} html object containing the created form
   */
  creationForm() {
    const formTemplate = Handlebars.compile(
      document.querySelector('#actor-form').innerHTML
    );
    const header = 'Create New Actor';
    let creationForm = formTemplate({ header });

    const div = document.createElement('div');
    div.innerHTML = creationForm;
    creationForm = div;

    creationForm.onsubmit = (event) => {
      event.preventDefault();
      const form = creationForm.lastElementChild;

      form.movies.setCustomValidity('');
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
   * @description Create a form to edit the actor
   * @return {Object} html object containing the created form
   */
  updateForm() {
    const formTemplate = Handlebars.compile(
      document.querySelector('#actor-form').innerHTML
    );
    const header = `Editing: ${this.name}`;
    const gender = {
      male: this.gender === 'male' ? 'selected' : '',
      female: this.gender === 'female' ? 'selected' : '',
    };
    const movies = this.movies.map((movie) => movie.title).join(',\n');
    let updateForm = formTemplate({
      header,
      name: this.name,
      birthdate: this.birthdate,
      gender,
      movies,
      image: this.image,
    });

    const div = document.createElement('div');
    div.innerHTML = updateForm;
    updateForm = div;

    updateForm.onsubmit = (event) => {
      event.preventDefault();
      const form = updateForm.lastElementChild;
      form.movies.setCustomValidity('');
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
   * @description Create a modal to view an actor
   * @return {Object} html object containing the created modal
   */
  modal() {
    const modalTemplate = Handlebars.compile(
      document.querySelector('#actor-modal').innerHTML
    );
    let { gender } = this;
    if (gender) {
      gender = this.gender.charAt(0).toUpperCase() + this.gender.slice(1);
    }
    let modal = modalTemplate({
      name: this.name,
      birthdate: this.birthdate,
      gender,
      image: this.image,
      movies: this.movies,
    });

    const div = document.createElement('div');
    div.innerHTML = modal;
    modal = div;

    if (auth.perms.includes('update:actors')) {
      const editBtn = modal.querySelector('#edit-btn');
      editBtn.classList.remove('hidden');
      editBtn.onclick = () => {
        const actorForm = this.updateForm();
        const modalContent = document.querySelector('.modal-content');
        modalContent.innerHTML = '';
        modalContent.appendChild(actorForm);
      };
    }

    if (auth.perms.includes('delete:actors')) {
      const deleteBtn = modal.querySelector('#delete-btn');
      deleteBtn.classList.remove('hidden');
      deleteBtn.onclick = () => {
        this.delete();
      };
    }

    return modal;
  }

  /**
   * @description Create a card to view an actor
   * @return {Object} html object containing the created card
   */
  card() {
    const cardTemplate = Handlebars.compile(
      document.querySelector('#actor-card').innerHTML
    );
    let { gender } = this;
    let age;
    if (this.birthdate) {
      age =
        new Date(Date.now() - Date.parse(this.birthdate)).getFullYear() - 1970;
    }
    if (gender) {
      gender = this.gender.charAt(0).toUpperCase() + this.gender.slice(1);
    }
    let card = cardTemplate({
      name: this.name,
      age,
      gender,
      image: this.image,
    });

    const div = document.createElement('div');
    div.innerHTML = card;
    card = div.firstElementChild;

    card.onclick = () => {
      const actorModal = this.modal();
      const modalContent = document.querySelector('.modal-content');
      modalContent.innerHTML = '';
      modalContent.appendChild(actorModal);
      $('#modal').modal('show');
    };

    return card;
  }
}

/**
 * @description Fetch actors and add them to the page
 * @param {number} page - page number to retrieve actors for
 */
export default function showActors(page) {
  const navActors = document.querySelector('#nav-actors');
  const navMovies = document.querySelector('#nav-movies');
  const modal = document.querySelector('#modal');
  const createBtn = document.querySelector('#create-btn');
  navActors.classList.add('active');
  navMovies.classList.remove('active');
  modal.classList.remove('movie-modal');
  modal.classList.add('actor-modal');

  if (auth.perms.includes('create:actors')) {
    createBtn.innerHTML = '&#10010; CREATE NEW ACTOR';
    createBtn.parentElement.classList.remove('hidden');
    createBtn.onclick = () => {
      const newActor = new Actor({}, showActors);
      const newActorForm = newActor.creationForm();
      const modalContent = document.querySelector('.modal-content');
      modalContent.innerHTML = '';
      modalContent.appendChild(newActorForm);
      $('#modal').modal('show');
    };
  } else {
    createBtn.parentElement.classList.add('hidden');
  }

  fetch(`/api/actors?page=${page}`, {
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
      data.actors.forEach((actor) => {
        const newActor = new Actor(actor, showActors);
        const actorCard = newActor.card();
        content.appendChild(actorCard);
      });

      const totalPages = Math.ceil(data.total_actors / 25);
      addPagination(totalPages, page, '/actors', showActors);
    })
    .catch(() => {
      flashMessage('danger', '&#10008; ERROR', 'An unknown error occurred!');
    });

  window.scrollTo(0, 0);
}
