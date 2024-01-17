describe('survivor spec', () => {
  it('can navigate from the home page to a survivor page', () => {
    cy.visit('/');
    cy.get('a[href*="survivor"]').first().click(); // get the first survivor link on the page (unless the DB for that season is empty)
    cy.url().should('match', /\/survivor\/\d\/*/) // survivor URL should look like /survivor/{id}/, where {id} is an integer representing their ID
  })
  it.skip('can login'), () => { // not written yet
    expect(true).to.equal(true)
  }
})