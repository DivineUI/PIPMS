def render_entity(entity_key):
    ent = ENTITIES[entity_key]
    st.markdown(f"""
    <div class="main-header">
        <h1>{ent["title"]}</h1>
        <p>{ent["desc"]}</p>
    </div>
    """, unsafe_allow_html=True)

    role = st.session_state.role
    can_create = can(role, entity_key, "c")
    can_update = can(role, entity_key, "u")
    can_delete = can(role, entity_key, "d")

    if st.session_state.confirm_delete and st.session_state.confirm_delete[0] == entity_key:
        _, pk = st.session_state.confirm_delete
        st.warning(f"Delete this {singular(ent['label']).lower()}? This cannot be undone.")
        cc1, cc2 = st.columns(2)
        if cc1.button("Yes, delete", type="primary", key=f"confirm_del_{entity_key}_{pk}"):
            try:
                database.execute(conn, f"DELETE FROM {entity_key} WHERE {ent['pk']} = ?", (pk,))
                st.success(f"{singular(ent['label'])} deleted.")
            except sqlite3.Error as e:
                st.error(friendly_sql_error(e))
            st.session_state.confirm_delete = None
            st.rerun()
        if cc2.button("Cancel", key=f"cancel_del_{entity_key}_{pk}"):
            st.session_state.confirm_delete = None
            st.rerun()
        return

    if st.session_state.form_mode and st.session_state.form_mode[1] == entity_key:
        render_form()
        return

    # Fetch rows first so we can use them for search, filtering, and CSV export
    rows = database.query(conn, ent["list_sql"])
    
    toolbar = st.columns([3] + [1] * len(ent["filters"]) + [1, 1])
    search_val = toolbar[0].text_input(f"Search {ent['label'].lower()}\u2026",
                                        value=st.session_state.search.get(entity_key, ""),
                                        key=f"search_{entity_key}", label_visibility="collapsed",
                                        placeholder=f"Search {ent['label'].lower()}\u2026")
    st.session_state.search[entity_key] = search_val

    active = st.session_state.active_filters.setdefault(entity_key, {})
    for i, f in enumerate(ent["filters"]):
        active[f["key"]] = toolbar[i + 1].checkbox(f["label"], value=active.get(f["key"], False),
                                                     key=f"filter_{entity_key}_{f['key']}")

    # Add button
    add_col_idx = len(ent["filters"]) + 1
    if can_create:
        if toolbar[add_col_idx].button(f"+ Add {singular(ent['label'])}", key=f"add_{entity_key}", type="primary", use_container_width=True):
            st.session_state.form_mode = ("add", entity_key, None, None)
            st.rerun()

    # Download CSV button
    download_col_idx = len(ent["filters"]) + 2
    if rows:
        df_export = pd.DataFrame(rows)
        csv_bytes = df_export.to_csv(index=False).encode('utf-8')
        toolbar[download_col_idx].download_button(
            label="📥 Download CSV",
            data=csv_bytes,
            file_name=f"{entity_key.lower()}_export.csv",
            mime="text/csv",
            key=f"download_btn_{entity_key}",
            use_container_width=True
        )

    # Filter/Search execution
    if search_val.strip():
        t = search_val.strip().lower()
        rows = [r for r in rows if any(t in str(r.get(k, "") or "").lower() for k in ent["search_keys"])]
    for f in ent["filters"]:
        if active.get(f["key"]):
            rows = [r for r in rows if f["test"](r)]

    st.caption(f"{len(rows)} record{'s' if len(rows) != 1 else ''}")
    render_table(ent, rows, entity_key, can_update, can_delete)
