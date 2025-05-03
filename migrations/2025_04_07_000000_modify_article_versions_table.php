<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::table('article_versions', function (Blueprint $table) {
            // Drop the existing primary key
            $table->dropPrimary();

            // Change version_id to string type
            $table->string('version_id', 100)->change();

            // Add new primary key
            $table->primary('version_id');
        });
    }

    public function down()
    {
        Schema::table('article_versions', function (Blueprint $table) {
            // Drop the primary key
            $table->dropPrimary();

            // Change version_id back to bigInteger
            $table->bigIncrements('version_id')->change();
        });
    }
};
