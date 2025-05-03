<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('article_versions', function (Blueprint $table) {
            $table->id('version_id');
            $table->unsignedBigInteger('article_id');
            $table->unsignedBigInteger('user_id');
            $table->text('title');
            $table->longText('content');
            $table->string('slug');
            $table->unsignedBigInteger('category_id')->nullable();
            $table->string('featured_image')->nullable();
            $table->json('tags')->nullable();
            $table->text('change_reason')->nullable();
            $table->timestamps();
            $table->foreign('article_id')->references('article_id')->on('articles')->onDelete('cascade');
            $table->foreign('user_id')->references('user_id')->on('users')->onDelete('cascade');
            $table->foreign('category_id')->references('category_id')->on('categories')->onDelete('set null');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('article_versions');
    }
};
