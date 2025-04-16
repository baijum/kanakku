import React, { useState, useEffect, useCallback } from 'react';

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page, setPage] = useState(0);
const [rowsPerPage, setRowsPerPage] = useState(10);
const [totalCount, setTotalCount] = useState(0);
const [error, setError] = useState('');
const [success, setSuccess] = useState('');
const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
const [accountToDelete, setAccountToDelete] = useState(null);

const [accounts, setAccounts] = useState([]);
const [page,