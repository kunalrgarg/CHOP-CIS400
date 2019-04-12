import React, { Component } from 'react';
import * as RB from 'react-bootstrap';
import ZoomableBurst from './zoomableBurst';
import { Modal } from 'react-bootstrap';

class Index extends Component {
  constructor(props, context) {
    super(props, context);

    this.clickHandler = this.clickHandler.bind(this);
    this.hideModal = this.hideModal.bind(this);

    this.state = {
      activeModal: null,
    };
  }

  clickHandler(e, index) {
    this.setState({ activeModal: index })
  }

  hideModal() {
      this.setState({ activeModal: null})
  }

  render() {
    const {
      updateSearchTerm,
      updateSearchType,
      requestSearch,
      searchTerm,
      searchType,
      results,
      requestRecs,
      recResults,
      recInProgress,
      inProgress } = this.props;

    const BUTTONS = ['Default']; // can add more buttons of various style

    function onSelectAlert(value) {
      updateSearchType(value);
    }

    function renderDropdownButton(title, i) {
      return (
        <RB.DropdownButton
          bsStyle={title.toLowerCase()}
          title={searchType}
          key={i}
          id={`dropdown-basic-${i}`}>
          <RB.MenuItem eventKey="Mesh"
            onSelect={onSelectAlert}>
              Mesh</RB.MenuItem>
          <RB.MenuItem eventKey="Author"
            onSelect={onSelectAlert}>
              Author</RB.MenuItem>
          <RB.MenuItem eventKey="Title"
            onSelect={onSelectAlert}>
              Title</RB.MenuItem>
          <RB.MenuItem divider />
          <RB.MenuItem eventKey="General Keyword"
            onSelect={onSelectAlert}>
            General Keyword
          </RB.MenuItem>
        </RB.DropdownButton>
      );
    }

    const typeButton = (
      <RB.ButtonToolbar>
        {BUTTONS.map(renderDropdownButton)}
      </RB.ButtonToolbar>
    );

    const viewRecResults = recInProgress ? <h4>loading</h4> : (recResults ?
     <div><h4>Recommendation Results (You Must Reload for Each New Author):</h4>
      <table><tbody><tr>
          <td width="40%">Name</td>
          <td width="20%">id</td>
          <td width="40%">weight</td></tr>
          {recResults['collaborators'].map((item, key) => {
            return (
              <tr key = {key}>
              <td width="40%">{item['author'].name}</td>
              <td width="20%">{item['author'].id}</td>
              <td width="40%">{item.weight}</td>
            </tr>)})}
        </tbody>
      </table></div> : <h4>Get Started By Hitting "Find Recs!"</h4>)

    function getRoleBadges(roles) {
      roles = roles.replace('[', '').replace(']', '').split(', ')
      const badgeTexts = [
        ['CA', 'Chief Author'],
        ['OA', 'Ordinary Author'],
        ['PI', 'Principal Investigator']
      ].filter(role => roles.indexOf('\'' + role[0] + '\'') >= 0).map(role =>
        '' + role[1] + ' (' + roles.filter(r => r == '\'' + role[0] + '\'').length + ')');
      return badgeTexts.map(t => <RB.Badge key={t} className={'badge-pill badge-' + (t.indexOf('Chief Author') >= 0 ?
        'success' : t.indexOf('Ordinary Author') >= 0 ? 'secondary' : 'primary')}
      >{t}</RB.Badge>)
    }

    const searchResultComponent = (results ?
      <div>
        <RB.Col xs={2} md={2} />
        <RB.Col xs={14} md={14}>
          <RB.Table striped bordered hover>
            <tbody>
              <tr>
                <td width="35%">Name</td>
                <td width="35%">Roles</td>
                <td width="20%">More Info</td>
              </tr>
              {results['authors'].map((item, key) => {
                return (
                  <tr key = {key}>
                    <td width="35%">{item.name}</td>
                    <td width="35%">{getRoleBadges(item.roles)}</td>
                    <td width="20%"><RB.Button onClick={e => this.clickHandler(e, key)}>View Recs</RB.Button></td>
                    <Modal id={key} show={this.state.activeModal === key} onHide={this.hideModal}>
                      <Modal.Header closeButton><Modal.Title>Recommendations for {item.name}</Modal.Title>
                      </Modal.Header>
                      <Modal.Body>{viewRecResults}</Modal.Body>
                      <Modal.Footer><RB.Button  onClick={() => requestRecs(item.id)}>Find Recs!</RB.Button>
                      </Modal.Footer>
                    </Modal>
                  </tr>)})}</tbody></RB.Table>
        </RB.Col>
        <RB.Col xs={2} md={2} />
      </div> : <h1>no results</h1>);

    return (
      <div>
        <RB.Grid>
          <RB.Row>
            <RB.Col xs={4} md={2} />
            <RB.Col xs={12} md={8}>
              <RB.PageHeader>
                MACRE: Medical and Academic Collaboration Recommendation Engine
                <br />
                <small>
                  by Santiago Buenahora, Garrett Darley, Kunal Garg, Nick Keenan
                </small>
              </RB.PageHeader>
              <form>
                <RB.FormGroup controlId='search'>
                  <RB.Grid>
                    <RB.Row className ="show-grid">
                      <RB.ControlLabel>Please enter a search term</RB.ControlLabel>
                    </RB.Row>
                    <RB.Row className ="show-grid">
                      <RB.Col xs={12} md={6}>
                        <RB.FormControl
                          value={searchTerm}
                          onChange={e => updateSearchTerm(e.target.value)}
                        />
                      </RB.Col>
                      <RB.Col xs={6} md={4}>
                        {typeButton}
                      </RB.Col>
                    </RB.Row>
                  </RB.Grid>
                  <RB.HelpBlock>This search term will be used for finding researcher data</RB.HelpBlock>
                  <RB.Grid>
                  </RB.Grid>
                </RB.FormGroup>
                <RB.Button onClick={() => requestSearch(searchTerm, searchType)}>{inProgress ? "Loading" : "Submit"}</RB.Button>
                <hr/>
              </form>
            </RB.Col>
            <RB.Col xs={4} md={2} />
          </RB.Row>
          <RB.Row>
            {results ? searchResultComponent : <div>
              <RB.Col xs={4} md={2} />
              <RB.Col xs={12} md={8}>
                <svg width={800} height={800}></svg>
              </RB.Col>
              <RB.Col xs={4} md={2} />
            </div>}
          </RB.Row>
          <ZoomableBurst/>
        </RB.Grid>
      </div>
    )
  }
}

export default Index;
